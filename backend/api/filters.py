from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilterSet(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(filters.FilterSet):
    BOOLEAN_CHOICES = (
        ('1', 'True'),
        ('0', 'False')
    )

    is_favorited = filters.ChoiceFilter(
        field_name='is_favorited_by',
        choices=BOOLEAN_CHOICES,
        method='filter_method_field')
    is_in_shopping_cart = filters.ChoiceFilter(
        field_name='in_shopping_list_of',
        choices=BOOLEAN_CHOICES,
        method='filter_method_field')
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all(),
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    def filter_method_field(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        query = Q(**{name: self.request.user})
        if value == '1':
            return queryset.filter(query)
        return queryset.filter(~query)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',
                  'author', 'tags')
