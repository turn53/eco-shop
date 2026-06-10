from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import UserProfile, Address, ViewHistory
from shop.models import Category, Product


class UserProfileModelTest(TestCase):
    """Тесты для модели UserProfile"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_profile_created_on_user_creation(self):
        """Тест автоматического создания профиля"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_profile_str(self):
        """Тест строкового представления профиля"""
        self.assertEqual(str(self.user.profile), f"Профиль {self.user.username}")

    def test_profile_favorite_categories(self):
        """Тест добавления любимых категорий"""
        category = Category.objects.create(name='Тестовая категория')
        self.user.profile.favorite_categories.add(category)
        self.assertEqual(self.user.profile.favorite_categories.count(), 1)


class AddressModelTest(TestCase):
    """Тесты для модели Address"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.address = Address.objects.create(
            user=self.user,
            title='Дом',
            recipient_name='Иван Иванов',
            phone='+79001234567',
            city='Москва',
            postal_code='123456',
            street='Тестовая улица',
            house='10',
            apartment='5',
            is_default=True
        )

    def test_address_creation(self):
        """Тест создания адреса"""
        self.assertEqual(self.address.title, 'Дом')
        self.assertEqual(self.address.city, 'Москва')
        self.assertTrue(self.address.is_default)

    def test_address_str(self):
        """Тест строкового представления адреса"""
        expected = "Дом - Москва, Тестовая улица, 10"
        self.assertEqual(str(self.address), expected)

    def test_address_full_address_property(self):
        """Тест свойства full_address"""
        full = self.address.full_address
        self.assertIn('Москва', full)
        self.assertIn('Тестовая улица', full)
        self.assertIn('10', full)
        self.assertIn('5', full)

    def test_only_one_default_address(self):
        """Тест установки только одного адреса по умолчанию"""
        address2 = Address.objects.create(
            user=self.user,
            title='Работа',
            recipient_name='Иван Иванов',
            phone='+79001234567',
            city='Москва',
            postal_code='654321',
            street='Рабочая улица',
            house='20',
            is_default=True
        )
        self.address.refresh_from_db()
        self.assertFalse(self.address.is_default)
        self.assertTrue(address2.is_default)


class ViewHistoryModelTest(TestCase):
    """Тесты для модели ViewHistory"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            category=self.category,
            name='Тестовый товар',
            price=Decimal('100.00'),
            stock=10
        )

    def test_view_history_creation(self):
        """Тест создания записи истории просмотров"""
        view = ViewHistory.objects.create(
            user=self.user,
            product=self.product
        )
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.product, self.product)
        self.assertIsNotNone(view.viewed_at)

    def test_view_history_str(self):
        """Тест строкового представления"""
        view = ViewHistory.objects.create(
            user=self.user,
            product=self.product
        )
        expected = f"{self.user.username} просмотрел {self.product.name}"
        self.assertEqual(str(view), expected)


class UserRegistrationViewTest(TestCase):
    """Тесты для представления регистрации"""

    def setUp(self):
        self.client = Client()

    def test_registration_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_registration_success(self):
        """Тест успешной регистрации"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Иван',
            'last_name': 'Иванов'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())


class UserLoginViewTest(TestCase):
    """Тесты для представления входа"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_login_view_get(self):
        """Тест GET запроса к странице входа"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_success(self):
        """Тест успешного входа"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        """Тест неуспешного входа"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserProfileViewTest(TestCase):
    """Тесты для представления профиля"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_profile_view_requires_login(self):
        """Тест требования авторизации для профиля"""
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated(self):
        """Тест доступа к профилю для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')


class OrderHistoryViewTest(TestCase):
    """Тесты для представления истории заказов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_order_history_requires_login(self):
        """Тест требования авторизации для истории заказов"""
        response = self.client.get(reverse('users:order_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_order_history_authenticated(self):
        """Тест доступа к истории заказов для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/order_history.html')
