from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('address/create/', views.address_create, name='address_create'),
    path('address/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('address/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
]
