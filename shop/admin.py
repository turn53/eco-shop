from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline для изображений товара"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    list_display = ['name', 'category', 'price', 'stock', 'is_available', 'is_featured', 'views_count', 'sales_count']
    list_filter = ['is_available', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description', 'material', 'manufacturer']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_available', 'is_featured']
    readonly_fields = ['views_count', 'sales_count', 'average_rating', 'reviews_count']
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'description', 'short_description')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock', 'is_available', 'is_featured')
        }),
        ('Характеристики экотовара', {
            'fields': ('eco_certificate', 'material', 'manufacturer', 'country')
        }),
        ('Статистика', {
            'fields': ('views_count', 'sales_count', 'average_rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Админка для изображений товаров"""
    list_display = ['product', 'is_main', 'order', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['product__name', 'alt_text']
