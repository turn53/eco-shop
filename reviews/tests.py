from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Review
from shop.models import Category, Product


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=Decimal('100.00'),
            stock=50
        )

    def test_review_creation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Отличный товар',
            text='Очень доволен покупкой',
            is_approved=True
        )
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_approved)


class ReviewViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=Decimal('100.00'),
            stock=50
        )

    def test_create_review_requires_login(self):
        response = self.client.get(reverse('reviews:create_review', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)

    def test_create_review_authenticated(self):
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('reviews:create_review', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
