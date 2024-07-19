import sys
import uuid

from django.db import models

from recipes.models import Recipe


def link_uri_default():
    id = uuid.uuid4()
    n = 3
    LinkModel = getattr(sys.modules[__name__], 'ShortLink')
    while (LinkModel.objects
                    .filter(link_uri=str(id).replace('-', '')[:n])
                    .exists()):
        n += 1
    return str(id).replace('-', '')[:n]


class ShortLink(models.Model):

    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        db_index=True
    )

    link_uri = models.CharField(
        max_length=36,
        unique=True,
        db_index=True,
        default=link_uri_default
    )
