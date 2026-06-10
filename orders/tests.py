from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem
from shop.models import Category, Product
from .services import CartService, OrderService


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertIsNotNone(self.cart.created_at)


class CartServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=Decimal('100.00'),
            stock=50
        )

    def test_get_or_create_cart(self):
        cart = CartService.get_or_create_cart(self.user)
        self.assertIsInstance(cart, Cart)

    def test_add_to_cart(self):
        cart_item = CartService.add_to_cart(self.user, self.product, 2)
        self.assertEqual(cart_item.quantity, 2)


class CartViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='test123')

    def test_cart_view_requires_login(self):
        response = self.client.get(reverse('orders:cart'))
        self.assertEqual(response.status_code, 302)

    def test_cart_view_authenticated(self):
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('orders:cart'))
        self.assertEqual(response.status_code, 200)
