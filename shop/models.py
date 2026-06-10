from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.utils.text import slugify


def transliterate(text):
    """Транслитерация кириллицы в латиницу для slug"""
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    return ''.join(translit_dict.get(char, char) for char in text)


class Category(models.Model):
    """Категория товаров"""
    name = models.CharField('Название', max_length=200, unique=True)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(transliterate(self.name))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Товар"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    description = models.TextField('Описание')
    short_description = models.CharField('Краткое описание', max_length=300, blank=True)
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField('Количество на складе', default=0)
    is_available = models.BooleanField('Доступен для заказа', default=True)
    is_featured = models.BooleanField('Рекомендуемый товар', default=False)

    # Характеристики экотовара
    eco_certificate = models.CharField('Эко-сертификат', max_length=200, blank=True)
    material = models.CharField('Материал', max_length=200, blank=True)
    manufacturer = models.CharField('Производитель', max_length=200, blank=True)
    country = models.CharField('Страна производства', max_length=100, blank=True)
    image_url = models.URLField('URL изображения', max_length=500, blank=True)

    # Статистика
    views_count = models.PositiveIntegerField('Просмотры', default=0)
    sales_count = models.PositiveIntegerField('Продажи', default=0)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_available', '-created_at']),
            models.Index(fields=['-sales_count']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(transliterate(self.name))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def in_stock(self):
        """Проверка наличия товара на складе"""
        return self.stock > 0

    @property
    def main_image(self):
        """Получить главное изображение товара"""
        return self.images.filter(is_main=True).first() or self.images.first()

    def get_image_url(self):
        """Получить URL изображения (либо загруженное, либо внешнее)"""
        main_img = self.main_image
        if main_img and main_img.image:
            return main_img.image.url
        return self.image_url if self.image_url else 'https://via.placeholder.com/400x300?text=No+Image'

    @property
    def average_rating(self):
        """Средний рейтинг товара"""
        from reviews.models import Review
        reviews = Review.objects.filter(product=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def reviews_count(self):
        """Количество отзывов"""
        from reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).count()


class ProductImage(models.Model):
    """Изображение товара"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    image = models.ImageField('Изображение', upload_to='products/')
    alt_text = models.CharField('Альтернативный текст', max_length=200, blank=True)
    is_main = models.BooleanField('Главное изображение', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order', '-is_main', '-created_at']

    def __str__(self):
        return f"Изображение для {self.product.name}"

    def save(self, *args, **kwargs):
        # Если это главное изображение, убрать флаг у других
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
