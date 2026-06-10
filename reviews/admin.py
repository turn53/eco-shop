from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для отзывов"""
    list_display = ['product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'text']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'user', 'rating', 'title', 'text')
        }),
        ('Детали', {
            'fields': ('pros', 'cons')
        }),
        ('Модерация', {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Одобрить выбранные отзывы'

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = 'Отклонить выбранные отзывы'
