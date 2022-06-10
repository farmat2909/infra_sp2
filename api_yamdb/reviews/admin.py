from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class BaseAdminSettings(admin.ModelAdmin):
    """Базовая кастомизация админ панели."""
    empty_value_display = '-пусто-'
    date_hierarchy = 'pub_date'
    list_filter = ('pub_date', 'author')


class ReviewAdmin(BaseAdminSettings):
    """Кастомизация админ панели (управление отзывами)."""
    list_display = (
        'id',
        'title',
        'text',
        'author',
        'score',
        'pub_date',
    )
    list_display_links = ('id', 'text', 'score')
    search_fields = ('author', 'title')


class CommentAdmin(BaseAdminSettings):
    """Кастомизация админ панели (управление отзывами)."""
    list_display = (
        'id',
        'review',
        'text',
        'author',
        'pub_date',
    )
    list_display_links = ('id', 'text')
    search_fields = ('author', 'review')


class CategoryGenreAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'name'
    )
    search_fields = ('slug',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category'
    )
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryGenreAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, CategoryGenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
