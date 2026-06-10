from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Category, Product, ProductImage


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Эко-посуда',
            description='Экологичная посуда',
            is_active=True
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Эко-посуда')
        self.assertTrue(self.category.is_active)
        self.assertIsNotNone(self.category.slug)

    def test_category_slug_generation(self):
        """Тест автогенерации slug"""
        self.assertEqual(self.category.slug, 'eko-posuda')

    def test_category_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.category), 'Эко-посуда')

    def test_category_get_absolute_url(self):
        """Тест получения URL категории"""
        url = self.category.get_absolute_url()
        self.assertIn('category', url)


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Тестовая категория',
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Бамбуковая тарелка',
            description='Экологичная тарелка',
            short_description='Эко тарелка',
            price=Decimal('450.00'),
            stock=50,
            is_available=True,
            material='Бамбук',
            manufacturer='ЭкоПроизводитель',
            country='Россия',
            eco_certificate='EcoCert',
            image_url='https://example.com/image.jpg'
        )

    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, 'Бамбуковая тарелка')
        self.assertEqual(self.product.price, Decimal('450.00'))
        self.assertEqual(self.product.stock, 50)
        self.assertTrue(self.product.is_available)

    def test_product_slug_generation(self):
        """Тест автогенерации slug"""
        self.assertIsNotNone(self.product.slug)
        self.assertIn('bambukovaya', self.product.slug)

    def test_product_in_stock_property(self):
        """Тест свойства in_stock"""
        self.assertTrue(self.product.in_stock)
        self.product.stock = 0
        self.assertFalse(self.product.in_stock)

    def test_product_get_image_url(self):
        """Тест получения URL изображения"""
        url = self.product.get_image_url()
        self.assertEqual(url, 'https://example.com/image.jpg')

    def test_product_get_image_url_fallback(self):
        """Тест fallback для изображения"""
        product = Product.objects.create(
            category=self.category,
            name='Тестовый товар без изображения',
            price=Decimal('100.00'),
            stock=10
        )
        url = product.get_image_url()
        self.assertIn('placeholder', url)

    def test_product_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.product), 'Бамбуковая тарелка')

    def test_product_average_rating_no_reviews(self):
        """Тест среднего рейтинга без отзывов"""
        self.assertEqual(self.product.average_rating, 0)

    def test_product_reviews_count_no_reviews(self):
        """Тест количества отзывов без отзывов"""
        self.assertEqual(self.product.reviews_count, 0)


class ProductListViewTest(TestCase):
    """Тесты для представления списка товаров"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Тестовая категория',
            is_active=True
        )
        for i in range(5):
            Product.objects.create(
                category=self.category,
                name=f'Товар {i}',
                description=f'Описание товара {i}',
                price=Decimal('100.00'),
                stock=10,
                is_available=True
            )

    def test_product_list_view_get(self):
        """Тест GET запроса к списку товаров"""
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
        self.assertIn('products', response.context)

    def test_product_list_view_shows_products(self):
        """Тест отображения товаров"""
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(len(response.context['products']), 5)

    def test_product_list_view_search(self):
        """Тест поиска товаров"""
        response = self.client.get(reverse('shop:product_list'), {'q': 'Товар 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Товар 1')

    def test_product_list_view_category_filter(self):
        """Тест фильтрации по категории"""
        response = self.client.get(
            reverse('shop:product_list'),
            {'category': self.category.slug}
        )
        self.assertEqual(response.status_code, 200)


class ProductDetailViewTest(TestCase):
    """Тесты для представления детальной информации о товаре"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Тестовая категория',
            is_active=True
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Тестовый товар',
            description='Описание',
            price=Decimal('500.00'),
            stock=20,
            is_available=True
        )

    def test_product_detail_view_get(self):
        """Тест GET запроса к странице товара"""
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')
        self.assertEqual(response.context['product'], self.product)

    def test_product_detail_view_returns_product(self):
        """Тест возвращения товара в контексте"""
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(response.context['product'], self.product)

    def test_product_detail_view_404(self):
        """Тест 404 для несуществующего товара"""
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': 'non-existent-slug'})
        )
        self.assertEqual(response.status_code, 404)


class AboutContactViewsTest(TestCase):
    """Тесты для страниц О нас и Контакты"""

    def setUp(self):
        self.client = Client()

    def test_about_view(self):
        """Тест страницы О нас"""
        response = self.client.get(reverse('shop:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/about.html')

    def test_contact_view(self):
        """Тест страницы Контакты"""
        response = self.client.get(reverse('shop:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/contact.html')
