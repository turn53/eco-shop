from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import RecommendationStats


@receiver(post_save, sender=Order)
def update_recommendation_stats(sender, instance, created, **kwargs):
    """Обновить статистику рекомендаций при оплаченном заказе"""
    if instance.is_paid:
        items = list(instance.items.filter(product__isnull=False))

        # Обновить статистику для каждой пары товаров в заказе
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                # Создать или обновить статистику для пары товаров
                stats, _ = RecommendationStats.objects.get_or_create(
                    product1=item1.product,
                    product2=item2.product
                )
                stats.frequency += 1
                stats.save()

                # Также создать обратную связь
                stats_reverse, _ = RecommendationStats.objects.get_or_create(
                    product1=item2.product,
                    product2=item1.product
                )
                stats_reverse.frequency += 1
                stats_reverse.save()
