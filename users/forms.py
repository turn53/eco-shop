from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Address


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(label='Имя пользователя или Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""
    class Meta:
        model = UserProfile
        fields = ('phone', 'birth_date', 'avatar', 'bio')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AddressForm(forms.ModelForm):
    """Форма адреса доставки"""
    class Meta:
        model = Address
        exclude = ('user',)
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
