import base64
from pathlib import Path
import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers

from recipes.models import Recipe_Ingredient


FORMAT_ERROR_MESSAGE = 'В поле изображения ожидается base64-строка'

BASE64_IMAGE_REGEX = (r'^data:image/(?P<format>[a-z]+);'
                      r'base64,(?P<image>[a-zA-Z0-9+/]+={,2})\Z')

LOCATIONS = {
    'avatar': settings.FOODGRAM.get('AVATAR_STORAGE'),
    'recipe': settings.FOODGRAM.get('IMAGE_STORAGE')
}


def get_image_from_base64(base64string, image_type):
    if not isinstance(base64string, str):
        raise serializers.ValidationError(FORMAT_ERROR_MESSAGE)
    regex_match = re.fullmatch(BASE64_IMAGE_REGEX, base64string)
    if not regex_match:
        raise serializers.ValidationError(FORMAT_ERROR_MESSAGE)
    format = regex_match.group('format')
    imgstr = regex_match.group('image')
    file_path = Path(
        default_storage.get_available_name(
            f'{LOCATIONS[image_type]}/img.{format}'
        )
    )
    file_obj = ContentFile(base64.b64decode(imgstr),
                           name=file_path.name)
    return file_obj


def shopping_list_as_dict(qset):
    ingr_amount = {}
    for recipe in qset:
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            amount = Recipe_Ingredient.objects.get(
                recipe=recipe,
                ingredient=ingredient
            ).amount
            if ingredient in ingr_amount:
                ingr_amount[ingredient] += amount
            else:
                ingr_amount[ingredient] = amount
    return ingr_amount


def fill_cart_file(ingr_amount, response):
    for ingredient, amount in ingr_amount.items():
        response.write(
            f'{ingredient.name}, {ingredient.measurement_unit} - {amount}\n'
        )
