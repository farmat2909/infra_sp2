from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


class ListCreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
