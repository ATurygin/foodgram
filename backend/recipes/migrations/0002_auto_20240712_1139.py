# Generated by Django 3.2.16 on 2024-07-12 07:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='coocking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть меньше 1')], verbose_name='Время приготовления'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='recipe_ingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
    ]
