from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Cart(models.Model):
    """Корзина пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_price(self):
        """Общая стоимость корзины"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Очистить корзину"""
        self.items.all().delete()


class CartItem(models.Model):
    """Элемент корзины"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Стоимость позиции"""
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возврат'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('yookassa', 'ЮКасса (банковская карта)'),
        ('cash', 'Наличными при получении'),
        ('card_on_delivery', 'Картой при получении'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name='Пользователь'
    )

    # Номер заказа
    order_number = models.CharField('Номер заказа', max_length=50, unique=True, blank=True)

    # Информация о получателе
    recipient_name = models.CharField('Имя получателя', max_length=200)
    recipient_phone = models.CharField('Телефон получателя', max_length=20)
    recipient_email = models.EmailField('Email получателя', blank=True)

    # Адрес доставки
    delivery_address = models.TextField('Адрес доставки')
    delivery_notes = models.TextField('Комментарий к заказу', blank=True)

    # Финансы
    subtotal = models.DecimalField('Сумма товаров', max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField('Стоимость доставки', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Итого к оплате', max_digits=10, decimal_places=2)

    # Статус и оплата
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_METHOD_CHOICES)
    is_paid = models.BooleanField('Оплачен', default=False)
    paid_at = models.DateTimeField('Дата оплаты', blank=True, null=True)

    # Даты
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Заказ №{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Генерация номера заказа
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD-{timestamp}"
        super().save(*args, **kwargs)

    @property
    def can_be_cancelled(self):
        """Можно ли отменить заказ"""
        return self.status in ['pending', 'paid', 'processing']

    @property
    def items_count(self):
        """Количество позиций в заказе"""
        return self.items.count()


class OrderItem(models.Model):
    """Элемент заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )
    product_name = models.CharField('Название товара', max_length=200)
    product_price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def total_price(self):
        """Стоимость позиции"""
        return self.product_price * self.quantity
