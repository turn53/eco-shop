from django.contrib import admin
from .models import RecommendationStats


@admin.register(RecommendationStats)
class RecommendationStatsAdmin(admin.ModelAdmin):
    """Админка для статистики рекомендаций"""
    list_display = ['product1', 'product2', 'frequency', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['product1__name', 'product2__name']
    readonly_fields = ['updated_at']
    ordering = ['-frequency']
