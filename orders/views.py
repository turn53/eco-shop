from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, Order
from .forms import CheckoutForm, CartItemUpdateForm
from .services import CartService, OrderService
from shop.models import Product


@login_required
def cart_view(request):
    """Просмотр корзины"""
    cart = CartService.get_or_create_cart(request.user)

    context = {
        'cart': cart,
    }
    return render(request, 'orders/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    try:
        CartService.add_to_cart(request.user, product, quantity)
        return JsonResponse({
            'success': True,
            'message': f'{product.name} добавлен в корзину!'
        })
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Обновить количество товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    try:
        CartService.update_cart_item(cart_item, quantity)
        messages.success(request, 'Количество обновлено!')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('orders:cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    CartService.remove_from_cart(cart_item)
    messages.success(request, 'Товар удалён из корзины!')
    return redirect('orders:cart')


@login_required
def checkout(request):
    """Оформление заказа"""
    cart = CartService.get_or_create_cart(request.user)

    if not cart.items.exists():
        messages.error(request, 'Ваша корзина пуста!')
        return redirect('orders:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            delivery_data = {
                'recipient_name': form.cleaned_data['recipient_name'],
                'recipient_phone': form.cleaned_data['recipient_phone'],
                'recipient_email': form.cleaned_data['recipient_email'],
                'delivery_address': form.cleaned_data['delivery_address'],
                'delivery_notes': form.cleaned_data['delivery_notes'],
            }
            payment_method = form.cleaned_data['payment_method']

            try:
                order = OrderService.create_order_from_cart(
                    cart, request.user, delivery_data, payment_method
                )
                messages.success(request, f'Заказ №{order.order_number} создан!')

                # Если оплата через ЮКассу, перенаправить на страницу оплаты
                if payment_method == 'yookassa':
                    return redirect('payments:create_payment', order_id=order.id)
                else:
                    return redirect('users:order_history')

            except ValueError as e:
                messages.error(request, str(e))
    else:
        # Предзаполнить данные из профиля
        initial = {
            'recipient_name': f'{request.user.first_name} {request.user.last_name}',
            'recipient_email': request.user.email,
        }
        if hasattr(request.user, 'profile') and request.user.profile.phone:
            initial['recipient_phone'] = request.user.profile.phone

        # Использовать адрес по умолчанию
        default_address = request.user.addresses.filter(is_default=True).first()
        if default_address:
            initial['delivery_address'] = default_address.full_address

        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@require_POST
def cancel_order(request, order_id):
    """Отменить заказ"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    try:
        OrderService.cancel_order(order)
        messages.success(request, f'Заказ №{order.order_number} отменён!')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('users:order_history')


def get_cart_count(request):
    """API endpoint для получения количества товаров в корзине"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})

    cart = CartService.get_or_create_cart(request.user)
    total_items = sum(item.quantity for item in cart.items.all())

    return JsonResponse({'count': total_items})
