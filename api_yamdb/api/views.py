from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from rest_framework import filters, viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.filters import FilterTitle
from api.permissions import (IsAdminOrReadOnly,
                             IsAdminModeratorAuthor,
                             AuthorOrAdmin
                             )
from api.mixins import ModelMixinSet
from api.serializers import (CategorySerializer,
                             GenreSerializer,
                             TitleReadSerializer,
                             TitleWriteSerializer,
                             CommentSerializer,
                             ReviewSerializer,
                             SignUpSerializer,
                             TokenSerializer,
                             UserSerializer
                             )
from api_yamdb.settings import ADMIN_EMAIL
from reviews.models import Category, Genre, Title, Review
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (AuthorOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('username',)
    search_fields = ('=username',)
    lookup_field = "username"
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    @action(methods=['GET', 'PATCH'],
            detail=False,
            url_path='me',
            permission_classes=(IsAuthenticated,))
    def me_profile(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        return Response(
            'Введите другие данные.',
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подтверждения', confirmation_code,
        [ADMIN_EMAIL], (email,), fail_silently=False
    )
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user_base = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user_base, confirmation_code):
        token = str(AccessToken.for_user(user_base))
        return Response({'token': token})
    return Response(
        {'message': 'Отказано в доступе'},
        status=status.HTTP_400_BAD_REQUEST
    )


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthor,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthor,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
