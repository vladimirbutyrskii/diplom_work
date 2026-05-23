from django.conf import settings
from django.db import models


class Ad(models.Model):
    """Модель объявления."""

    title = models.CharField('Название товара', max_length=200)
    price = models.PositiveIntegerField('Цена товара')
    description = models.TextField('Описание товара', blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Автор объявления',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']  # Сортировка: чем новее, тем выше

    def __str__(self):
        return f'{self.title} — {self.price} ₽'


class Comment(models.Model):
    """Модель отзыва."""

    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор отзыва',
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Объявление',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.author.email} на {self.ad.title}'

