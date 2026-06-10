from django.db import models


class RecommendationStats(models.Model):
    """Статистика для рекомендательной системы - товары, которые часто покупают вместе"""
    product1 = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='recommendations_from',
        verbose_name='Товар 1'
    )
    product2 = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='recommendations_to',
        verbose_name='Товар 2'
    )
    frequency = models.PositiveIntegerField(
        'Частота совместных покупок',
        default=1,
        help_text='Количество раз, когда товары были куплены вместе'
    )
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Статистика рекомендаций'
        verbose_name_plural = 'Статистика рекомендаций'
        unique_together = ['product1', 'product2']
        indexes = [
            models.Index(fields=['product1', '-frequency']),
            models.Index(fields=['product2', '-frequency']),
        ]

    def __str__(self):
        return f"{self.product1.name} + {self.product2.name} ({self.frequency})"
