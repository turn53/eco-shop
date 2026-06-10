from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/<int:order_id>/', views.create_payment, name='create_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('webhook/', views.yookassa_webhook, name='yookassa_webhook'),
    path('check/<uuid:payment_id>/', views.check_payment_status, name='check_payment_status'),
]
