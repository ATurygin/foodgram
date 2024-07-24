from django.contrib import admin
from django.contrib.admin.decorators import display

from .models import Ingredient, Recipe, Recipe_Ingredient, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):
    model = Recipe_Ingredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date',
                    'cooking_time', 'image')
    list_editable = ('image',)
    search_fields = ('name', 'author__username',
                     'author__first_name',
                     'author__last_name')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (IngredientsInline,)
    date_hierarchy = 'pub_date'
    readonly_fields = ('times_favorited', 'pub_date')

    @display(description='Добавлен в избранное')
    def times_favorited(self, obj):
        return obj.is_favorited_by.count()


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
