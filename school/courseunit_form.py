# CourseUnitForm to be added to forms.py

from django import forms
from .models import CourseUnit


class CourseUnitForm(forms.ModelForm):
    """Form for adding/editing course units"""
    class Meta:
        model = CourseUnit
        fields = ['title', 'code', 'description', 'credits', 'semester', 'instructor', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit Title'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101-U1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Unit Description'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instructor Name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
