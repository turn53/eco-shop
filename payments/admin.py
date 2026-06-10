from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка для платежей"""
    list_display = ['payment_id', 'order', 'user', 'amount', 'currency', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['payment_id', 'yookassa_payment_id', 'order__order_number', 'user__username']
    readonly_fields = ['payment_id', 'created_at', 'updated_at', 'paid_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('payment_id', 'yookassa_payment_id', 'order', 'user')
        }),
        ('Финансы', {
            'fields': ('amount', 'currency', 'status')
        }),
        ('Данные ЮКассы', {
            'fields': ('confirmation_url', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
