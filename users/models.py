from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    phone = PhoneNumberField('Телефон', blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', blank=True)

    # Предпочтения для рекомендаций
    favorite_categories = models.ManyToManyField(
        'shop.Category',
        verbose_name='Любимые категории',
        blank=True
    )

    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"Профиль {self.user.username}"


class Address(models.Model):
    """Адрес доставки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Пользователь'
    )
    title = models.CharField('Название адреса', max_length=100, help_text='Например: Дом, Работа')
    recipient_name = models.CharField('Имя получателя', max_length=200)
    phone = PhoneNumberField('Телефон получателя')

    # Адрес
    country = models.CharField('Страна', max_length=100, default='Россия')
    city = models.CharField('Город', max_length=100)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    street = models.CharField('Улица', max_length=200)
    house = models.CharField('Дом', max_length=20)
    apartment = models.CharField('Квартира/офис', max_length=20, blank=True)
    entrance = models.CharField('Подъезд', max_length=10, blank=True)
    floor = models.CharField('Этаж', max_length=10, blank=True)
    intercom = models.CharField('Домофон', max_length=20, blank=True)

    notes = models.TextField('Комментарий к адресу', blank=True)
    is_default = models.BooleanField('Адрес по умолчанию', default=False)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.city}, {self.street}, {self.house}"

    def save(self, *args, **kwargs):
        # Если это адрес по умолчанию, убрать флаг у других адресов пользователя
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Полный адрес в одной строке"""
        parts = [
            self.postal_code,
            self.city,
            f"ул. {self.street}",
            f"д. {self.house}",
        ]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        return ", ".join(parts)


class ViewHistory(models.Model):
    """История просмотров товаров пользователем"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='view_history',
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name='Товар'
    )
    viewed_at = models.DateTimeField('Дата просмотра', auto_now_add=True)

    class Meta:
        verbose_name = 'История просмотра'
        verbose_name_plural = 'История просмотров'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} просмотрел {self.product.name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создать профиль при регистрации пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранить профиль при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
