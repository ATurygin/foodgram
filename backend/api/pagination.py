from django.conf import settings
from rest_framework.pagination import PageNumberPagination

DEFAULT_PAGE_SIZE = settings.FOODGRAM['DEFAULT_PAGE_SIZE']


class FoodgramPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
