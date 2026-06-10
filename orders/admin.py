from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    """Inline для элементов корзины"""
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админка для корзин"""
    list_display = ['user', 'total_items', 'total_price', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'total_items']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    """Inline для элементов заказа"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""
    list_display = ['order_number', 'user', 'recipient_name', 'status', 'payment_method', 'is_paid', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid', 'created_at']
    search_fields = ['order_number', 'user__username', 'recipient_name', 'recipient_phone']
    date_hierarchy = 'created_at'
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'is_paid', 'paid_at')
        }),
        ('Получатель', {
            'fields': ('recipient_name', 'recipient_phone', 'recipient_email')
        }),
        ('Доставка', {
            'fields': ('delivery_address', 'delivery_notes')
        }),
        ('Финансы', {
            'fields': ('subtotal', 'delivery_cost', 'total')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_paid', 'mark_as_shipped']

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True, status='paid')
    mark_as_paid.short_description = 'Отметить как оплаченные'

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = 'Отметить как отправленные'
