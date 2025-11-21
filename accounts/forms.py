from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import (
    Account, ContactMessage, Wishlist, 
    UserProfile, Category
)


# ============ REGISTRATION FORM ============
class RegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        })
    )
    
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        })
    )
    
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = Account
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Account.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2


# ============ USER FORM ============
class UserForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )
    
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )
    
    phone_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number',
        })
    )
    
    role = forms.ChoiceField(
        choices=Account.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role')


# ============ ACCOUNT CREATION FORM ============
class AccountCreationForm(UserCreationForm):
    """
    Form for creating a new account (admin)
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email',
        })
    )
    
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )
    
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )

    class Meta:
        model = Account
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')


# ============ ACCOUNT CHANGE FORM ============
class AccountChangeForm(UserChangeForm):
    """
    Form for updating account information
    """
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'role')


# ============ CONTACT FORM ============
class ContactForm(forms.ModelForm):
    """
    Contact form for user inquiries
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email',
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message',
            'rows': 5,
        })
    )

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')





# ============ WISHLIST FORM ============
class WishlistForm(forms.ModelForm):
    """
    Form for adding items to wishlist
    """
    product_id = forms.CharField(
        max_length=100,
        widget=forms.HiddenInput()
    )
    
    product_name = forms.CharField(
        max_length=255,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Wishlist
        fields = ('product_id', 'product_name')





# ============ USER PROFILE FORM ============
class UserProfileForm(forms.ModelForm):
    """
    Form for updating user trading profile
    """
    account_level = forms.ChoiceField(
        choices=UserProfile.ACCOUNT_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    notification_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    two_factor_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = UserProfile
        fields = ('account_level', 'notification_email', 'two_factor_enabled')


# ============ PASSWORD CHANGE FORM ============
class PasswordChangeForm(forms.Form):
    """
    Form for changing password
    """
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter old password',
            'autocomplete': 'current-password',
        })
    )
    
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        })
    )
    
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('New passwords do not match.')
        return cleaned_data


# ============ DERIV CONNECTION FORM ============
class DerivConnectionForm(forms.Form):
    """
    Form for connecting Deriv account
    """
    api_token = forms.CharField(
        label='Deriv API Token',
        max_length=255,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Deriv API token',
            'autocomplete': 'off',
        })
    )
    
    confirm = forms.BooleanField(
        label='I confirm this is a valid Deriv API token',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    def clean_api_token(self):
        api_token = self.cleaned_data.get('api_token')
        if len(api_token) < 10:
            raise ValidationError('API token is too short. Please verify.')
        return api_token


# ============ SEARCH FORM ============
class SearchForm(forms.Form):
    """
    General search form
    """
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'autocomplete': 'off',
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )


# ============ CATEGORY FORM ============
class CategoryForm(forms.ModelForm):
    """
    Form for creating/updating categories
    """
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Category name',
        })
    )
    
    slug = forms.SlugField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Slug (auto-generated)',
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Category description',
            'rows': 4,
        })
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = Category
        fields = ('name', 'slug', 'description', 'image', 'is_active')