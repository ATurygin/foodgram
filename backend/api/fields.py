from rest_framework import serializers

from .utils import get_image_from_base64


class Base64ImageField(serializers.ImageField):

    def __init__(self, *args, **kwargs):
        image_type = kwargs.pop('image_type')
        super().__init__(*args, **kwargs)
        self.image_type = image_type

    def to_internal_value(self, data):
        file = get_image_from_base64(data, self.image_type)
        return super().to_internal_value(file)
