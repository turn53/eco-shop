from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from shop.models import Product
from .utils import (
    get_popular_products,
    get_similar_products,
    get_frequently_bought_together,
    get_recommendations_for_cart,
    get_recommendations_for_user
)


def get_recommendations(request):
    """Получить рекомендации для чат-бота"""
    recommendation_type = request.GET.get('type', 'popular')
    limit = int(request.GET.get('limit', 6))

    products = []

    if recommendation_type == 'popular':
        products = get_popular_products(limit)

    elif recommendation_type == 'for_user' and request.user.is_authenticated:
        products = get_recommendations_for_user(request.user, limit)

    elif recommendation_type == 'for_cart' and request.user.is_authenticated:
        from orders.services import CartService
        cart = CartService.get_or_create_cart(request.user)
        if cart:
            products = get_recommendations_for_cart(cart.items.all(), limit)
        else:
            products = get_popular_products(limit)

    elif recommendation_type == 'similar':
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                products = get_similar_products(product, limit)
            except Product.DoesNotExist:
                products = get_popular_products(limit)

    elif recommendation_type == 'bought_together':
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                products = get_frequently_bought_together(product, limit)
            except Product.DoesNotExist:
                products = get_popular_products(limit)

    else:
        products = get_popular_products(limit)

    # Сформировать JSON ответ
    recommendations = []
    for product in products:
        recommendations.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'url': product.get_absolute_url(),
            'image': product.main_image.image.url if product.main_image else None,
            'rating': product.average_rating,
        })

    return JsonResponse({
        'recommendations': recommendations,
        'count': len(recommendations)
    })
