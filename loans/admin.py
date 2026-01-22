from django.contrib import admin
from django.utils.html import format_html
from .models import LoanApplication, LoanDocument, LoanVerification


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'national_id', 'status_badge', 'loan_amount', 'created_at', 'days_pending']
    list_filter = ['status', 'created_at', 'verified_at']
    search_fields = ['first_name', 'last_name', 'email', 'national_id', 'phone_number']
    readonly_fields = ['user', 'created_at', 'updated_at', 'verified_by', 'verified_at', 'disbursed_at', 'rejected_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'middle_name', 'last_name')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Identity', {
            'fields': ('national_id', 'id_image')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address', 'city', 'county', 'postal_code')
        }),
        ('Institution', {
            'fields': ('institution', 'institution_id')
        }),
        ('Loan Details', {
            'fields': ('loan_amount', 'loan_tenure', 'purpose')
        }),
        ('Status', {
            'fields': ('status', 'verification_notes', 'rejection_reason')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at')
        }),
        ('Disbursement', {
            'fields': ('bank_name', 'account_number', 'disbursed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_pending', 'mark_verified', 'mark_rejected']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Applicant Name'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'FFC107',
            'verified': '28A745',
            'disbursed': '0066CC',
            'rejected': 'DC3545',
            'cancelled': '6C757D'
        }
        color = colors.get(obj.status, '6C757D')
        return format_html(
            '<span style="background-color: #{}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, 'Selected applications marked as pending.')
    mark_pending.short_description = 'Mark selected as Pending'
    
    def mark_verified(self, request, queryset):
        queryset.update(status='verified', verified_by=request.user, verified_at=timezone.now())
        self.message_user(request, 'Selected applications marked as verified.')
    mark_verified.short_description = 'Mark selected as Verified'
    
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected', rejected_at=timezone.now())
        self.message_user(request, 'Selected applications marked as rejected.')
    mark_rejected.short_description = 'Mark selected as Rejected'


@admin.register(LoanDocument)
class LoanDocumentAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['application__first_name', 'application__last_name']
    readonly_fields = ['uploaded_at']


@admin.register(LoanVerification)
class LoanVerificationAdmin(admin.ModelAdmin):
    list_display = ['application', 'step', 'status', 'verified_by', 'verified_at']
    list_filter = ['step', 'status', 'verified_at']
    search_fields = ['application__first_name', 'application__last_name']
    readonly_fields = ['verified_at']


from django.utils import timezone
