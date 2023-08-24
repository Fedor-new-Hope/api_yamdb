from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.settings import EMAIL_MAX_LENGTH


class User(AbstractUser):
    USER_ROLE = ('user', 'юзер')
    MODERATOR_ROLE = ('moderator', 'модератор')
    ADMIN_ROLE = ('admin', 'админ')

    CHOICES = (
        USER_ROLE,
        MODERATOR_ROLE,
        ADMIN_ROLE
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=50,
        choices=CHOICES,
        default='user',
    )
    confirmation_code = models.CharField(
        verbose_name='Токен пользователя',
        max_length=100,
        blank=True,
        null=True,
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELDS = 'email'

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return str(self.username)

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
