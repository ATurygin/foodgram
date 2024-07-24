from django.conf import settings

COOCKING_TIME_ERR_MSG = 'Время приготовления не может быть меньше 1'

AMOUNT_ERR_MSG = 'Amount не может быть меньше 1'

IMAGE_STORAGE = settings.FOODGRAM.get('IMAGE_STORAGE')
