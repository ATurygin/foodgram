from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

AVATAR_STORAGE = settings.FOODGRAM.get('AVATAR_STORAGE')


class FoodgramUserManager(UserManager):

    def create_user(self, username, email, password,
                    first_name, last_name, **extra_fields):
        return super().create_user(username, email, password,
                                   first_name=first_name,
                                   last_name=last_name,
                                   **extra_fields)

    def create_superuser(self, username, email, password,
                         first_name, last_name, **extra_fields):
        return super().create_superuser(username, email, password,
                                        first_name=first_name,
                                        last_name=last_name,
                                        **extra_fields)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email-адрес',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким Email уже существует',
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to=AVATAR_STORAGE,
        blank=True,
        null=True
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Избранное',
        related_name='is_favorited_by'
    )
    shopping_list = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Список покупок',
        related_name='in_shopping_list_of'
    )
    subscriptions = models.ManyToManyField(
        'self',
        verbose_name='Подписки',
        symmetrical=False
    )

    USERNAME_FIELD = 'email'

    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    objects = FoodgramUserManager()

    class Meta(AbstractUser.Meta):
        ordering = ['username']
        indexes = [
            models.Index(fields=['email'])
        ]

    def __str__(self):
        return self.username
