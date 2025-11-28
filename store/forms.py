from django import forms

from CDMIS.models import Order
from .models import ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']





class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'  # Or specify the fields you want, e.g. ['field1', 'field2']