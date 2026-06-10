from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
from orders.models import Order
from .services import YooKassaService


@login_required
def create_payment(request, order_id):
    """Создать платеж для заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, 'Этот заказ уже оплачен!')
        return redirect('users:order_history')

    try:
        service = YooKassaService()
        payment_data = service.create_payment(order)

        # Перенаправить на страницу оплаты ЮКассы
        return redirect(payment_data['confirmation_url'])

    except ValueError as e:
        messages.error(request, f'Ошибка создания платежа: {e}')
        return redirect('orders:order_detail', order_id=order.id)
    except Exception as e:
        messages.error(request, f'Произошла ошибка: {e}')
        return redirect('orders:order_detail', order_id=order.id)


def payment_success(request):
    """Страница успешной оплаты"""
    return render(request, 'payments/success.html')


def payment_failed(request):
    """Страница неудачной оплаты"""
    return render(request, 'payments/failed.html')


@csrf_exempt
def yookassa_webhook(request):
    """Webhook для уведомлений от ЮКассы"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        service = YooKassaService()
        success = service.handle_webhook(data)

        if success:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)

    except Exception:
        return HttpResponse(status=500)


@login_required
def check_payment_status(request, payment_id):
    """Проверить статус платежа"""
    from .models import Payment

    payment = get_object_or_404(Payment, payment_id=payment_id)

    # Проверить, принадлежит ли платеж пользователю
    if payment.order.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому платежу')
        return redirect('shop:product_list')

    try:
        service = YooKassaService()
        status = service.check_payment_status(payment)

        return JsonResponse({
            'status': status,
            'is_paid': payment.is_paid
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
