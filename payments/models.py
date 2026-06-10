from django.db import models
from django.contrib.auth.models import User
import uuid


class Payment(models.Model):
    """Платеж через ЮКассу"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('waiting_for_capture', 'Ожидает подтверждения'),
        ('succeeded', 'Успешно оплачен'),
        ('canceled', 'Отменен'),
        ('failed', 'Не удался'),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Заказ'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )

    # Идентификаторы
    payment_id = models.UUIDField('ID платежа', default=uuid.uuid4, editable=False, unique=True)
    yookassa_payment_id = models.CharField('ID платежа в ЮКассе', max_length=100, blank=True)

    # Сумма
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3, default='RUB')

    # Статус
    status = models.CharField('Статус', max_length=30, choices=STATUS_CHOICES, default='pending')

    # URL для возврата
    confirmation_url = models.URLField('URL для оплаты', blank=True)

    # Метаданные
    metadata = models.JSONField('Метаданные', default=dict, blank=True)

    # Даты
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    paid_at = models.DateTimeField('Дата оплаты', blank=True, null=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['yookassa_payment_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Платеж {self.payment_id} - {self.amount} {self.currency}"

    @property
    def is_paid(self):
        """Проверка, оплачен ли платеж"""
        return self.status == 'succeeded'
