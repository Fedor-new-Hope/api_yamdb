from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from api_yamdb.settings import NAME_MAX_LENGTH, SLUG_MAX_LENGTH

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            null=False,
                            verbose_name='Имя жанра',)
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            unique=True,
                            verbose_name='Slug жанра')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Имя категории',)
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            unique=True,
                            db_index=True,
                            verbose_name='Slug категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} {self.name}'


class Title(models.Model):
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    year = models.IntegerField('Год выпуска',
                               blank=True,)
    description = models.TextField('Описание',
                                   null=True,
                                   blank=True)
    genre = models.ManyToManyField(Genre,
                                   related_name='GenreTitle',
                                   verbose_name='Slug жанра',)
    category = models.ForeignKey(Category,
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='titles',
                                 verbose_name='Slug категории',)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название'
    )
    score = models.PositiveSmallIntegerField(verbose_name='Оценка отзыва',
                                             validators=[MinValueValidator(1),
                                                         MaxValueValidator(10)]
                                             )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique reviews',
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
