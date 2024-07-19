from django.urls import re_path

from api.views import RecipeLinkView

urlpatterns = [
    re_path(
        r's/(?P<slug>\w+)/',
        RecipeLinkView.as_view(),
        name='recipe-link'
    )
]
