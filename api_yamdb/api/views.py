from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL
from reviews.models import Category, Genre, Title
from users.models import User, UserRole
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (AuthorOrAdminOrModeratorOrReadOnly, IsAdmin,
                          IsAdminOrReadOnly, IsSuperUser)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SendConfirmationCodeSerializer, SendTokenSerializer,
                          TitlePostSerializer, TitleSerializer,
                          UpdateSelfSerializer, UserSerializer)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Класс категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    """Класс жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведений."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = TitleFilter
    search_fields = ('name', 'year', 'category', 'genre')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializer
        return TitlePostSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Класс пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, IsSuperUser)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'],
            url_path='me', permission_classes=[IsAuthenticated])
    def get_or_update_self(self, request):
        """
        Функция обрабатывает 'GET' и 'PATCH' запросы на эндпоинт '/users/me/'
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data)
        serializer = UpdateSelfSerializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        user_email = User.objects.filter(email=email).exists()
        user_username = User.objects.filter(username=username).exists()

        data_of_me = self.get_serializer(request.user, many=False)

        if user_email and email != data_of_me.data.get('email'):
            message = {'email': f'{email} уже зарегистрирован'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if user_username and username != data_of_me.data.get('username'):
            message = {'username': f'{username} уже зарегистрирован'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if (data_of_me.data.get('role') == UserRole.USER
                and 'role' in request.data):
            message = {'role': 'user'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение и создание отзывов."""
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrAdminOrModeratorOrReadOnly,)

    def get_titles_obj(self, title_id):
        """Получение объектов произведений."""
        return get_object_or_404(Title, pk=self.kwargs.get(title_id))

    def get_queryset(self):
        title = self.get_titles_obj('title_id')
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_titles_obj('title_id')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Получение и создание комментариев."""
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrAdminOrModeratorOrReadOnly,)

    def get_reviews_obj(self, title_obj_id, review_obj_id):
        """Получение объектов отзывов."""
        title = get_object_or_404(Title, pk=self.kwargs.get(title_obj_id))
        return title.reviews.all().get(pk=self.kwargs.get(review_obj_id))

    def get_queryset(self):
        review = self.get_reviews_obj('title_id', 'review_id')
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_reviews_obj('title_id', 'review_id')
        serializer.save(author=self.request.user, review=review)


def send_email(email):
    user = get_object_or_404(User, email=email)
    confirmation_code = default_token_generator.make_token(user)
    User.objects.filter(email=email).update(
        confirmation_code=confirmation_code
    )
    send_mail(
        subject='Ваш код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """
    Функция обрабатывает POST-запрос для регистрации нового пользователя и
    получаения кода подтверждения, который необходим для получения JWT-токена.
    На вход подается 'username' и 'email', а в ответ происходит отправка
    на почту письма с кодом подтверждения.
    """
    serializer = SendConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    user_email = User.objects.filter(email=email).exists()
    user_username = User.objects.filter(username=username).exists()

    if user_email:
        message = {'email': f'{email} уже зарегистрирован.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if user_username:
        message = {'username': f'{username} уже зарегистрирован.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if not (user_email or user_username):
        User.objects.create_user(email=email, username=username)
        send_email(email)
        message = {'email': email, 'username': username}
        return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token(request):
    """
    Функция обрабатывает POST-запрос для получаения JWT-токена.
    На вход подается 'username' и 'confirmation_code',
    а в ответ формируется JWT-токен.
    """
    serializer = SendTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    token = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, token):
        message = {'confirmation_code': 'Неверный код подтверждения'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    message = {'token': str(AccessToken.for_user(user))}
    return Response(message, status=status.HTTP_200_OK)
