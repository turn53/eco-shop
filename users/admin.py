from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Address, ViewHistory


class UserProfileInline(admin.StackedInline):
    """Inline для профиля пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'


class AddressInline(admin.TabularInline):
    """Inline для адресов доставки"""
    model = Address
    extra = 0
    fields = ['title', 'city', 'street', 'house', 'apartment', 'is_default']


class CustomUserAdmin(BaseUserAdmin):
    """Расширенная админка для пользователей"""
    inlines = (UserProfileInline, AddressInline)


# Перерегистрируем модель User с кастомным админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Админка для адресов"""
    list_display = ['user', 'title', 'city', 'full_address', 'is_default', 'created_at']
    list_filter = ['is_default', 'city', 'created_at']
    search_fields = ['user__username', 'recipient_name', 'city', 'street']
    date_hierarchy = 'created_at'


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    """Админка для истории просмотров"""
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'product__name']
    date_hierarchy = 'viewed_at'
    readonly_fields = ['user', 'product', 'viewed_at']
