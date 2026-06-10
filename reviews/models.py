from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Отзыв о товаре"""
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField('Заголовок', max_length=200, blank=True)
    text = models.TextField('Текст отзыва')

    # Плюсы и минусы
    pros = models.TextField('Достоинства', blank=True)
    cons = models.TextField('Недостатки', blank=True)

    # Модерация
    is_approved = models.BooleanField('Одобрен', default=False)
    is_verified_purchase = models.BooleanField('Подтвержденная покупка', default=False)

    # Даты
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name} ({self.rating}★)"
