from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from .models import Address
from orders.models import Order


def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('shop:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'shop:product_list')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('shop:product_list')


@login_required
def profile(request):
    """Профиль пользователя"""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён успешно!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'addresses': user.addresses.all()
    }
    return render(request, 'users/profile.html', context)


@login_required
def address_create(request):
    """Создание нового адреса"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Адрес добавлен успешно!')
            return redirect('users:profile')
    else:
        form = AddressForm()
    return render(request, 'users/address_form.html', {'form': form})


@login_required
def address_edit(request, pk):
    """Редактирование адреса"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Адрес обновлён успешно!')
            return redirect('users:profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'users/address_form.html', {'form': form})


@login_required
def address_delete(request, pk):
    """Удаление адреса"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Адрес удалён успешно!')
    return redirect('users:profile')


class OrderHistoryView(LoginRequiredMixin, ListView):
    """История заказов пользователя"""
    model = Order
    template_name = 'users/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')
