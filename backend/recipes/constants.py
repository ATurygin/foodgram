from django.conf import settings

IMAGE_STORAGE = settings.FOODGRAM.get('IMAGE_STORAGE')

COOCKING_TIME_ERR_MSG = 'Время приготовления не может быть меньше 1'

AMOUNT_ERR_MSG = 'Amount не может быть меньше 1'

TAG_NAME_MAX_LENGTH = 64

TAG_SLUG_MAX_LENGTH = 64

INGREDIENT_NAME_MAX_LENGTH = 256

INGREDIENT_UNIT_MAX_LENGTH = 32

RECIPE_NAME_MAX_LENGTH = 256
