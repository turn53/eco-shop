from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Payment
from orders.models import Order


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.order = Order.objects.create(
            user=self.user,
            recipient_name='Test',
            recipient_phone='+79001234567',
            recipient_email='test@test.com',
            delivery_address='Test Address',
            payment_method='yookassa',
            subtotal=Decimal('1000.00'),
            delivery_cost=Decimal('0.00'),
            total=Decimal('1000.00')
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('1000.00'),
            status='pending'
        )
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.status, 'pending')

    def test_payment_is_paid_property(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('1000.00'),
            status='succeeded'
        )
        self.assertTrue(payment.is_paid)


class PaymentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.order = Order.objects.create(
            user=self.user,
            recipient_name='Test',
            recipient_phone='+79001234567',
            recipient_email='test@test.com',
            delivery_address='Test Address',
            payment_method='yookassa',
            subtotal=Decimal('1000.00'),
            delivery_cost=Decimal('0.00'),
            total=Decimal('1000.00')
        )

    def test_payment_success_view(self):
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('payments:payment_success'))
        self.assertEqual(response.status_code, 200)
