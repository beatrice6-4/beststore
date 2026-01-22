from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import LoanApplication, LoanDocument


class LoanApplicationForm(ModelForm):
    """Form for loan application submission"""
    
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
        label="Latitude"
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
        label="Longitude"
    )
    
    class Meta:
        model = LoanApplication
        fields = [
            'first_name', 'middle_name', 'last_name',
            'phone_number', 'email',
            'national_id', 'id_image',
            'address', 'city', 'county', 'postal_code',
            'latitude', 'longitude',
            'institution', 'institution_id',
            'loan_amount', 'loan_tenure', 'purpose'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254712345678',
                'required': True,
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'required': True
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'National ID / Passport Number',
                'required': True
            }),
            'id_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,application/pdf',
                'required': True,
                'capture': 'environment'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full residential address',
                'rows': 2
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County/Region'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company/University/School',
                'required': True
            }),
            'institution_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee/Student ID'
            }),
            'loan_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Loan amount in KES',
                'required': True,
                'min': 1000,
                'step': 100
            }),
            'loan_tenure': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Loan duration in months',
                'required': True,
                'min': 1,
                'max': 60,
                'value': 12
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Purpose of the loan',
                'rows': 3,
                'required': True
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already has an application
            from django.contrib.auth.models import User
            user = self.instance.user if hasattr(self.instance, 'user') else None
            existing = LoanApplication.objects.filter(email=email).exclude(user=user).exists()
            if existing:
                raise forms.ValidationError("This email already has an active loan application.")
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id:
            # Check if ID already has an application
            existing = LoanApplication.objects.filter(national_id=national_id).exclude(pk=self.instance.pk).exists()
            if existing:
                raise forms.ValidationError("This National ID already has an active loan application.")
        return national_id


class LoanDocumentForm(ModelForm):
    """Form for uploading additional loan documents"""
    
    class Meta:
        model = LoanDocument
        fields = ['document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'document_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
                'required': True
            })
        }


# Formset for multiple documents
LoanDocumentFormSet = inlineformset_factory(
    LoanApplication,
    LoanDocument,
    form=LoanDocumentForm,
    extra=2,
    can_delete=True,
    min_num=0
)


class LoanVerificationForm(forms.Form):
    """Form for admin verification"""
    
    verification_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add verification notes here',
            'rows': 3
        }),
        required=False
    )
    
    status = forms.ChoiceField(
        choices=[
            ('verified', 'Approve Application'),
            ('rejected', 'Reject Application'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        required=True
    )
    
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Reason for rejection (if rejected)',
            'rows': 2
        }),
        required=False
    )


class LoanDisbursementForm(forms.Form):
    """Form for loan disbursement"""
    
    bank_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank Name',
            'required': True
        })
    )
    
    account_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account Number',
            'required': True
        })
    )
    
    account_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account Holder Name',
            'required': True
        })
    )
    
    disbursement_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Disbursement notes',
            'rows': 2
        }),
        required=False
    )


class LoanFilterForm(forms.Form):
    """Form for filtering loans"""
    
    STATUS_CHOICES = [('', 'All Status')] + LoanApplication.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, email...'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
