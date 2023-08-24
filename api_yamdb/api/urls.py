from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet, ReviewViewSet, CommentViewSet,
                       get_token,
                       sign_up, UserViewSet
                       )

router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/auth/signup/', sign_up, name='signup'),
    path('v1/auth/token/', get_token, name='get_token'),
    path('v1/', include(router.urls)),
]
