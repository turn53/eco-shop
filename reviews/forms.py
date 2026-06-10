from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""
    class Meta:
        model = Review
        fields = ('rating', 'title', 'text', 'pros', 'cons')
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} звезд') for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'rows': 4}),
            'pros': forms.Textarea(attrs={'rows': 2}),
            'cons': forms.Textarea(attrs={'rows': 2}),
        }
