from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'product', 'amount', 'status']

from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'registration_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

# forms.py
from django import forms

class MemberUploadForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

from django import forms
from .models import Requirement

class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ['title', 'description']