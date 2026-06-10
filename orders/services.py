"""
Сервисы для работы с корзиной и заказами
"""
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem


class CartService:
    """Сервис для работы с корзиной"""

    @staticmethod
    def get_or_create_cart(user):
        """Получить или создать корзину для пользователя"""
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            return cart
        return None

    @staticmethod
    def add_to_cart(user, product, quantity=1):
        """Добавить товар в корзину"""
        cart = CartService.get_or_create_cart(user)
        if not cart:
            return None

        # Проверить наличие товара
        if not product.is_available or product.stock < quantity:
            raise ValueError("Товар недоступен или недостаточно на складе")

        # Добавить или обновить товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Обновить количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                raise ValueError("Недостаточно товара на складе")
            cart_item.quantity = new_quantity
            cart_item.save()

        return cart_item

    @staticmethod
    def update_cart_item(cart_item, quantity):
        """Обновить количество товара в корзине"""
        if quantity <= 0:
            cart_item.delete()
            return None

        if quantity > cart_item.product.stock:
            raise ValueError("Недостаточно товара на складе")

        cart_item.quantity = quantity
        cart_item.save()
        return cart_item

    @staticmethod
    def remove_from_cart(cart_item):
        """Удалить товар из корзины"""
        cart_item.delete()

    @staticmethod
    def clear_cart(cart):
        """Очистить корзину"""
        cart.clear()


class OrderService:
    """Сервис для работы с заказами"""

    @staticmethod
    def create_order_from_cart(cart, user, delivery_data, payment_method):
        """
        Создать заказ из корзины

        Args:
            cart: Корзина
            user: Пользователь
            delivery_data: Данные о доставке (dict)
            payment_method: Способ оплаты

        Returns:
            Order: Созданный заказ
        """
        if not cart.items.exists():
            raise ValueError("Корзина пуста")

        # Проверить наличие всех товаров
        for item in cart.items.all():
            if not item.product.is_available:
                raise ValueError(f"Товар {item.product.name} недоступен")
            if item.product.stock < item.quantity:
                raise ValueError(f"Недостаточно товара {item.product.name} на складе")

        # Рассчитать стоимость
        subtotal = cart.total_price

        # Стоимость доставки (можно добавить логику расчета)
        delivery_cost = Decimal('0.00')
        if subtotal < 3000:  # Бесплатная доставка от 3000 руб
            delivery_cost = Decimal('300.00')

        total = subtotal + delivery_cost

        # Создать заказ
        order = Order.objects.create(
            user=user,
            recipient_name=delivery_data.get('recipient_name'),
            recipient_phone=delivery_data.get('recipient_phone'),
            recipient_email=delivery_data.get('recipient_email', ''),
            delivery_address=delivery_data.get('delivery_address'),
            delivery_notes=delivery_data.get('delivery_notes', ''),
            subtotal=subtotal,
            delivery_cost=delivery_cost,
            total=total,
            payment_method=payment_method,
            is_paid=False
        )

        # Создать элементы заказа
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity
            )

        # Очистить корзину
        cart.clear()

        return order

    @staticmethod
    def cancel_order(order):
        """Отменить заказ"""
        if not order.can_be_cancelled:
            raise ValueError("Заказ нельзя отменить")

        order.status = 'cancelled'
        order.save()

        # Вернуть товары на склад
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.sales_count = max(0, item.product.sales_count - item.quantity)
                item.product.save()

        return order
