from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import RecommendationStats
from shop.models import Category, Product


class RecommendationStatsModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test')
        self.product1 = Product.objects.create(
            category=self.category,
            name='Product 1',
            price=Decimal('100.00'),
            stock=50
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name='Product 2',
            price=Decimal('200.00'),
            stock=30
        )

    def test_recommendation_stats_creation(self):
        stat = RecommendationStats.objects.create(
            product1=self.product1,
            product2=self.product2,
            frequency=10
        )
        self.assertEqual(stat.frequency, 10)
        self.assertEqual(stat.product1, self.product1)

    def test_recommendation_stats_str(self):
        stat = RecommendationStats.objects.create(
            product1=self.product1,
            product2=self.product2,
            frequency=10
        )
        self.assertIn(self.product1.name, str(stat))
        self.assertIn(self.product2.name, str(stat))
