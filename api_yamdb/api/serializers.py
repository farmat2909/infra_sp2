from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

SCORE = [i for i in range(1, 11)]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category',)


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    year = serializers.IntegerField(
        validators=(
            MinValueValidator(0, message='Год не может быть больше меньше 0!'),
            MaxValueValidator(timezone.now().year,
                              message='Год не может быть больше текущего!'),
        )
    )

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'description',
                  'genre',
                  'category',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        ref_name = 'ReadOnlyUsers'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if value not in SCORE:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне 1-10.'
            )
        return value

    def validate(self, data):
        if not self.context.get('request').method == 'POST':
            return data

        author = self.context.get('request').user
        title = self.context.get('view').kwargs.get(['title_id'][0])

        if Review.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError(
                'Нельзя добавить больше одного отзыва!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели комментариев."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SendConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        max_length=150, required=True, regex=r"^[\w.@+-]+\Z"
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                f'Некорректный username = "{value}"'
            )
        return value


class SendTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150, required=True, regex=r"^[\w.@+-]+\Z"
    )
    confirmation_code = serializers.CharField(required=True)


class UpdateSelfSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=False)
    username = serializers.RegexField(
        max_length=150, required=False, regex=r"^[\w.@+-]+\Z"
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio'
        )
