from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FoodgramUserDetailViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    TagViewSet,
                    UserAvatarView)

router = DefaultRouter()
router.register(r'users', FoodgramUserDetailViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'users/me/avatar/',
         UserAvatarView.as_view(),
         name='user-avatar')
]
