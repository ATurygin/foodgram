from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Recipe_Ingredient, Tag
from .fields import Base64ImageField

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FoodgramUserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        return obj in self.context['request'].user.subscriptions.all()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(image_type='avatar', required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeIngredientReadOnlySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = Recipe_Ingredient
        fields = ('id', 'name', 'measurement_unit',
                  'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    author = FoodgramUserDetailSerializer(read_only=True)
    image = serializers.ImageField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                  'name', 'image', 'text',
                  'cooking_time', 'tags',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return self.context['request'].user in obj.is_favorited_by.all()

    def get_is_in_shopping_cart(self, obj):
        return self.context['request'].user in obj.in_shopping_list_of.all()

    def get_ingredients(self, obj):
        qset = Recipe_Ingredient.objects.filter(
            recipe=obj
        )
        return [
            RecipeIngredientReadOnlySerializer(instance=record).data
            for record in qset
        ]


class RecipeIngredientWhriteOnlySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Recipe_Ingredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    INGREDIENTS_EMPTY_ERROR = ('Поле ingredients является обязательным!')
    TAGS_EMPTY_ERROR = ('Поле tags является обязательным!')
    NON_UNIQUE_TAG_ERROR = ('Значения в поле tags не должны повторяться!')
    NON_UNIQUE_INGREDIENT_ERROR = ('Значения в поле ingredients'
                                   ' не должны повторяться!')

    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    ingredients = RecipeIngredientWhriteOnlySerializer(
        read_only=False,
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        read_only=False
    )
    image = Base64ImageField(image_type='recipe')

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                  'name', 'image', 'text',
                  'cooking_time', 'tags')

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                self.INGREDIENTS_EMPTY_ERROR
            )
        ingredient_amount = {}
        for ingredient in data:
            if ingredient['id'] in ingredient_amount:
                raise serializers.ValidationError(
                    self.NON_UNIQUE_INGREDIENT_ERROR
                )
            ingredient_amount[ingredient['id']] = ingredient['amount']
        return ingredient_amount

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                self.TAGS_EMPTY_ERROR
            )
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                self.NON_UNIQUE_TAG_ERROR
            )
        return data

    def validate(self, attrs):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                self.INGREDIENTS_EMPTY_ERROR
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                self.TAGS_EMPTY_ERROR
            )
        return super().validate(attrs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_obj, amount in ingredients.items():
            Recipe_Ingredient.objects.create(recipe=recipe,
                                             ingredient=ingredient_obj,
                                             amount=amount)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if 'image' in validated_data:
            instance.image.delete(save=True)
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient_obj, amount in ingredients.items():
            Recipe_Ingredient.objects.create(recipe=instance,
                                             ingredient=ingredient_obj,
                                             amount=amount)
        return instance


class RecipeUpdateSerializer(RecipeCreateSerializer):
    image = Base64ImageField(image_type='recipe', required=False)

    class Meta(RecipeCreateSerializer.Meta):
        pass


class RecipeFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(FoodgramUserDetailSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(FoodgramUserDetailSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',
                  'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        qset = obj.recipes.all()
        page_size = self.context['request'].query_params.get(
            'recipes_limit',
            None
        )
        paginated_qset = None
        if page_size:
            try:
                paginator = Paginator(qset, page_size)
                paginated_qset = paginator.get_page(1)
            except Exception:
                paginated_qset = None
        serializer = RecipeFavoriteSerializer(
            paginated_qset or qset,
            many=True
        )
        return serializer.data
