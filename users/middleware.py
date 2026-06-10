"""
Middleware для отслеживания просмотров товаров
"""
from django.utils.deprecation import MiddlewareMixin
from shop.models import Product
from users.models import ViewHistory


class ProductViewMiddleware(MiddlewareMixin):
    """Middleware для отслеживания просмотров товаров"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Отследить просмотр товара"""
        # Проверить, что это просмотр детальной страницы товара
        if view_func.__name__ == 'product_detail' and request.user.is_authenticated:
            slug = view_kwargs.get('slug')
            if slug:
                try:
                    product = Product.objects.get(slug=slug)

                    # Проверить, был ли уже просмотр недавно (в течение 1 часа)
                    from django.utils import timezone
                    from datetime import timedelta

                    recent_view = ViewHistory.objects.filter(
                        user=request.user,
                        product=product,
                        viewed_at__gte=timezone.now() - timedelta(hours=1)
                    ).exists()

                    if not recent_view:
                        # Создать запись о просмотре
                        ViewHistory.objects.create(
                            user=request.user,
                            product=product
                        )

                        # Увеличить счетчик просмотров товара
                        Product.objects.filter(pk=product.pk).update(
                            views_count=product.views_count + 1
                        )

                except Product.DoesNotExist:
                    pass

        return None
