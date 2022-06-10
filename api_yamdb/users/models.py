from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class UserRole:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    choices = [
        (USER, 'USER'),
        (ADMIN, 'ADMIN'),
        (MODERATOR, 'MODERATOR'),
    ]


class User(AbstractUser):
    """Модель пользователей."""
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name='Username'
    )
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.TextField(max_length=150, blank=True)
    last_name = models.TextField(max_length=150, blank=True)
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.TextField(
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Пользовательская роль'
    )
    confirmation_code = models.TextField(default='000000')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'Пользователи'
