from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from .constants import (AMOUNT_ERR_MSG,
                        COOCKING_TIME_ERR_MSG,
                        IMAGE_STORAGE,
                        INGREDIENT_NAME_MAX_LENGTH,
                        INGREDIENT_UNIT_MAX_LENGTH,
                        RECIPE_NAME_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH,
                        TAG_SLUG_MAX_LENGTH,)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_NAME_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'
        ordering = ['slug']

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['name', 'measurement_unit'],
                             name='unique_ingredient')
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, message=COOCKING_TIME_ERR_MSG)]
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to=IMAGE_STORAGE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='Recipe_Ingredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.author} - {self.name}'


class Recipe_Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message=AMOUNT_ERR_MSG)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'
        constraints = [
            UniqueConstraint(fields=['recipe', 'ingredient'],
                             name='unique_recipe_ingredient')
        ]
