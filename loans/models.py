from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, FileExtensionValidator
from datetime import timedelta

class LoanApplication(models.Model):
    """Model for loan applications"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('disbursed', 'Disbursed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # User Information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    
    # Contact Information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be entered in the format: +999999999')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    email = models.EmailField()
    
    # Identity Information
    national_id = models.CharField(max_length=50, unique=True, help_text="National ID/Passport Number")
    id_image = models.ImageField(
        upload_to='loans/id_scans/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        help_text="Upload scanned image of your national ID"
    )
    
    # Location Information
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Institution Information
    institution = models.CharField(max_length=200, help_text="Educational/Employment Institution")
    institution_id = models.CharField(max_length=100, blank=True)
    
    # Loan Details
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    loan_tenure = models.IntegerField(help_text="Loan tenure in months", default=12)
    purpose = models.TextField(help_text="Purpose of the loan")
    
    # Status Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin Verification
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_loans')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, help_text="Admin notes during verification")
    
    # Disbursement
    disbursed_at = models.DateTimeField(null=True, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    
    # Rejection
    rejection_reason = models.TextField(blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['national_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_geolocation(self):
        """Return geolocation as tuple"""
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None
    
    def is_pending(self):
        return self.status == 'pending'
    
    def is_verified(self):
        return self.status == 'verified'
    
    def is_disbursed(self):
        return self.status == 'disbursed'
    
    @property
    def days_pending(self):
        """Calculate days since application was created"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days


class LoanDocument(models.Model):
    """Additional supporting documents for loan application"""
    
    DOCUMENT_TYPES = [
        ('employment_letter', 'Employment Letter'),
        ('pay_slip', 'Pay Slip'),
        ('bank_statement', 'Bank Statement'),
        ('income_certificate', 'Income Certificate'),
        ('other', 'Other Document'),
    ]
    
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='loans/documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.application.get_full_name()} - {self.get_document_type_display()}"


class LoanVerification(models.Model):
    """Track verification steps for auditing"""
    
    VERIFICATION_STEPS = [
        ('identity_check', 'Identity Verification'),
        ('income_verification', 'Income Verification'),
        ('employment_check', 'Employment Check'),
        ('geolocation_check', 'Geolocation Verification'),
        ('credit_check', 'Credit Check'),
        ('final_approval', 'Final Approval'),
    ]
    
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='verifications')
    step = models.CharField(max_length=50, choices=VERIFICATION_STEPS)
    status = models.CharField(max_length=20, choices=[('passed', 'Passed'), ('failed', 'Failed'), ('pending', 'Pending')])
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-verified_at']
        unique_together = ['application', 'step']
    
    def __str__(self):
        return f"{self.application.get_full_name()} - {self.get_step_display()}: {self.status}"
