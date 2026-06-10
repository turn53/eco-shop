from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_product_sales_count(sender, instance, created, **kwargs):
    """Обновить счетчик продаж товаров при создании заказа"""
    if created and instance.is_paid:
        for item in instance.items.all():
            if item.product:
                item.product.sales_count += item.quantity
                item.product.stock -= item.quantity
                item.product.save()
