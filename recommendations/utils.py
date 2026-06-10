from django.conf import settings
from django.db.models import Count, Q
from shop.models import Product
from .models import RecommendationStats


def get_popular_products(limit=None):
    """Получить популярные товары (по количеству продаж)"""
    if limit is None:
        limit = settings.RECOMMENDATIONS_LIMIT
    return Product.objects.filter(
        is_available=True
    ).order_by('-sales_count', '-views_count')[:limit]


def get_similar_products(product, limit=None):
    """Получить похожие товары (из той же категории)"""
    if limit is None:
        limit = settings.RECOMMENDATIONS_LIMIT
    return Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id).order_by('-sales_count')[:limit]


def get_frequently_bought_together(product, limit=None):
    """Получить товары, которые часто покупают вместе"""
    if limit is None:
        limit = settings.RECOMMENDATIONS_LIMIT

    # Получить статистику рекомендаций для данного товара
    stats = RecommendationStats.objects.filter(
        product1=product
    ).select_related('product2').order_by('-frequency')[:limit]

    return [stat.product2 for stat in stats if stat.product2.is_available]


def get_recommendations_for_cart(cart_items, limit=None):
    """Получить рекомендации на основе товаров в корзине"""
    if limit is None:
        limit = settings.RECOMMENDATIONS_LIMIT

    if not cart_items:
        return get_popular_products(limit)

    # Собрать все продукты из корзины
    cart_product_ids = [item.product.id for item in cart_items if item.product]

    if not cart_product_ids:
        return get_popular_products(limit)

    # Найти товары, которые часто покупают с товарами из корзины
    recommended_stats = RecommendationStats.objects.filter(
        product1__id__in=cart_product_ids
    ).exclude(
        product2__id__in=cart_product_ids
    ).filter(
        product2__is_available=True
    ).select_related('product2').order_by('-frequency')[:limit * 2]

    # Убрать дубликаты и ограничить количество
    seen = set()
    recommendations = []
    for stat in recommended_stats:
        if stat.product2.id not in seen:
            seen.add(stat.product2.id)
            recommendations.append(stat.product2)
            if len(recommendations) >= limit:
                break

    # Если рекомендаций мало, добавить популярные товары
    if len(recommendations) < limit:
        popular = get_popular_products(limit - len(recommendations))
        for product in popular:
            if product.id not in seen and product.id not in cart_product_ids:
                recommendations.append(product)

    return recommendations[:limit]


def get_recommendations_for_user(user, limit=None):
    """Получить персональные рекомендации для пользователя на основе истории"""
    if limit is None:
        limit = settings.RECOMMENDATIONS_LIMIT

    if not user.is_authenticated:
        return get_popular_products(limit)

    # Получить последние просмотренные товары
    from users.models import ViewHistory
    recent_views = ViewHistory.objects.filter(
        user=user
    ).select_related('product').order_by('-viewed_at')[:10]

    if not recent_views:
        return get_popular_products(limit)

    # Собрать товары на основе истории просмотров
    viewed_product_ids = [view.product.id for view in recent_views]

    # Найти похожие товары
    recommended_stats = RecommendationStats.objects.filter(
        product1__id__in=viewed_product_ids
    ).exclude(
        product2__id__in=viewed_product_ids
    ).filter(
        product2__is_available=True
    ).select_related('product2').order_by('-frequency')[:limit * 2]

    seen = set()
    recommendations = []
    for stat in recommended_stats:
        if stat.product2.id not in seen:
            seen.add(stat.product2.id)
            recommendations.append(stat.product2)
            if len(recommendations) >= limit:
                break

    # Дополнить популярными товарами если нужно
    if len(recommendations) < limit:
        popular = get_popular_products(limit - len(recommendations))
        for product in popular:
            if product.id not in seen and product.id not in viewed_product_ids:
                recommendations.append(product)

    return recommendations[:limit]
