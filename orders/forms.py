from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Форма оформления заказа"""
    class Meta:
        model = Order
        fields = (
            'recipient_name',
            'recipient_phone',
            'recipient_email',
            'delivery_address',
            'delivery_notes',
            'payment_method'
        )
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'delivery_notes': forms.Textarea(attrs={'rows': 2}),
        }


class CartItemUpdateForm(forms.Form):
    """Форма обновления количества товара в корзине"""
    quantity = forms.IntegerField(min_value=1, label='Количество')
