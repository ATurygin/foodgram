from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Ingredient, Recipe, Tag
from .decorators import m2m_set, m2m_unset
from .filters import IngredientFilterSet, RecipeFilterSet
from .models import ShortLink
from .pagination import FoodgramPagination
from .permissions import AuthorOrStaffOrReadOnly
from .serializers import (AvatarSerializer,
                          FoodgramUserDetailSerializer,
                          IngredientSerializer,
                          RecipeCreateSerializer,
                          RecipeFavoriteSerializer,
                          RecipeReadOnlySerializer,
                          RecipeUpdateSerializer,
                          SubscriptionSerializer,
                          TagSerializer)
from .utils import (fill_cart_file,
                    shopping_list_as_dict)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class FoodgramUserDetailViewSet(UserViewSet):
    ALREADY_SUBSCRIBED_ERROR = 'Вы уже подписаны на данного пользователя.'
    SELF_SUBSCRIPTION_ERROR = 'Вы не можете подписаться на себя!'
    DELETE_NONEXIST_SUBSCRIPTION = 'Вы не подписаны на данного пользователя.'
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FoodgramUserDetailSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return SubscriptionSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    @m2m_set('subscriptions', ALREADY_SUBSCRIBED_ERROR)
    def subscribe(self, request, id=None):
        if request.user == self.get_object():
            raise ValidationError(self.SELF_SUBSCRIPTION_ERROR)

    @subscribe.mapping.delete
    @m2m_unset('subscriptions', DELETE_NONEXIST_SUBSCRIPTION)
    def unsubscribe(self, request, id=None):
        return

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        qset = request.user.subscriptions.all()
        page = self.paginate_queryset(qset)
        if page is not None:
            serializer = self.get_serializer(page,
                                             many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qset,
                                         many=True,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.user.avatar is not None:
            request.user.avatar.delete(save=True)
        serializer = AvatarSerializer(request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    RECIPE_ALREADY_IN_FAVORITES = 'Рецепт уже есть в избранном.'
    DELETE_NONEXIST_FAVORITE = 'Указанного рецепта нет в избранном.'
    RECIPE_ALREADY_IN_SHOPPING_CART = 'Рецепт уже есть в корзине покупок.'
    DELETE_NONEXIST_SHOPPING_CART = 'Указанного рецепта нет в корзине покупок.'

    queryset = Recipe.objects.select_related('author')
    http_method_names = ['get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace']
    permission_classes = [AuthorOrStaffOrReadOnly]
    pagination_class = FoodgramPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action in ('update', 'partial_update'):
            return RecipeUpdateSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeFavoriteSerializer
        return RecipeReadOnlySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        responce_serializer = RecipeReadOnlySerializer(
            instance=instance,
            context={'request': request}
        )
        headers = self.get_success_headers(responce_serializer.data)
        return Response(responce_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.image.delete(save=True)
        instance.delete()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        responce_serializer = RecipeReadOnlySerializer(
            instance=instance,
            context={'request': request}
        )
        return Response(responce_serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    @m2m_set('favorites', RECIPE_ALREADY_IN_FAVORITES)
    def favorite(self, request, pk=None):
        instance = self.get_object()
        instance.times_favorited += 1
        instance.save()

    @favorite.mapping.delete
    @m2m_unset('favorites', DELETE_NONEXIST_FAVORITE)
    def delete_from_fovorites(self, request, pk=None):
        return

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        cart = request.user.shopping_list.all()
        ingr_amount = shopping_list_as_dict(cart)
        response = HttpResponse(
            'Список покупок: \n',
            headers={
                'Content-Type': 'text/plain;charset=UTF-8',
                "Content-Disposition":
                    'attachment; filename="shopping_list.txt"'
            }
        )
        fill_cart_file(ingr_amount, response)
        return response

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    @m2m_set('shopping_list', RECIPE_ALREADY_IN_SHOPPING_CART)
    def shopping_cart(self, request, pk=None):
        return

    @shopping_cart.mapping.delete
    @m2m_unset('shopping_list', DELETE_NONEXIST_SHOPPING_CART)
    def delete_from_shopping_cart(self, request, pk=None):
        return

    @action(detail=True,
            methods=['get'],
            url_path='get-link',
            permission_classes=[AllowAny])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not hasattr(recipe, 'shortlink'):
            ShortLink.objects.create(recipe=recipe)
        domain = settings.FOODGRAM['REDIRECT_URL']
        url = (f'{domain}/'
               f's/{recipe.shortlink.link_uri}/')
        data = {'short-link': url}
        return Response(data, status=status.HTTP_200_OK)


class RecipeLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        link_obj = get_object_or_404(ShortLink, link_uri=slug)
        domain = settings.FOODGRAM['REDIRECT_URL']
        url = (f'{domain}/'
               f'recipes/{link_obj.recipe.id}')
        return redirect(url)
