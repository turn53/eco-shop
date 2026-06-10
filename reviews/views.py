from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Product
from .models import Review
from .forms import ReviewForm


@login_required
def create_review(request, product_id):
    """Создать отзыв на товар"""
    product = get_object_or_404(Product, id=product_id)

    # Проверить, не оставил ли пользователь уже отзыв
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.warning(request, 'Вы уже оставили отзыв на этот товар!')
        return redirect('shop:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user

            # Проверить, покупал ли пользователь этот товар
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                order__is_paid=True,
                product=product
            ).exists()
            review.is_verified_purchase = has_purchased

            review.save()
            messages.success(request, 'Спасибо за отзыв! Он будет опубликован после модерации.')
            return redirect('shop:product_detail', slug=product.slug)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'reviews/create_review.html', context)
