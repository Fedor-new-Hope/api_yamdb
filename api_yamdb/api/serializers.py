from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api_yamdb.settings import USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH
from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id', )
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError(
                'Может быть только один отзыв.'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
    )
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            RegexValidator(r'^[\w.@+-]+$',)]
    )

    def validate(self, value):
        if not User.objects.filter(
                username=value.get('username'),
                email=value.get('email')).exists():
            if User.objects.filter(username=value.get('username')):
                raise ValidationError(
                    'Пользователь с таким именем уже существует.'
                )
            if User.objects.filter(email=value.get('email')):
                raise ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return value

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError(
                'Запрещено имя "me", придумайте другое имя.')
        return value

    class Meta:
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
