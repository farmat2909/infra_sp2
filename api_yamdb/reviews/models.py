from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils import timezone

from users.models import User


class Category(models.Model):
    """Модель категорий."""
    name = models.CharField(
        max_length=256,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message='Slug должен состоять из набора латинских букв и цифр',
            ),
        ]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель жанров."""
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(
        max_length=100,
        verbose_name='Произведение',
    )
    year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Год выхода',
        validators=(MaxValueValidator(
            timezone.now().year,
            message='Год не может быть больше текущего!'),)
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        ordering = ('-year', 'name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов."""
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    title = models.ForeignKey(
        Title,
        null=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]

    def __str__(self) -> str:
        return self.text


class Comment(models.Model):
    """Модель комментариев."""
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата аубликации'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text
