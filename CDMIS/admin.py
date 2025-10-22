from django.contrib import admin
from django.http import HttpResponse
import csv
from CDMIS.models import (
    Group, Payment, Activity, Training, Service, Update, Booking, Requirement, Document, FinancialAccount, Withdrawal
)

# Register Group, Activity, Training, and Service models
admin.site.register(Group)
admin.site.register(Activity)
admin.site.register(Training)
admin.site.register(Service)


# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('group', 'amount', 'payment_date', 'notes')
    actions = ['download_payments_csv']

    def download_payments_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=payments.csv'
        writer = csv.writer(response)
        writer.writerow(['Group', 'Amount', 'Date', 'Recorded By', 'Notes'])
        for payment in queryset:
            writer.writerow([
                payment.group.name,
                payment.amount,
                payment.payment_date,
                payment.added_by.username if payment.added_by else '',
                payment.notes
            ])
        return response

    download_payments_csv.short_description = "Download selected payments as CSV"


# Requirement Admin
@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)


# Document Admin
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')
    search_fields = ('title',)


# Update Admin
@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_by')
    search_fields = ('title', 'content')
    list_filter = ('date', 'created_by')
    actions = ['download_updates_csv']

    def download_updates_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=updates.csv'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Content', 'Date', 'Created By'])
        for update in queryset:
            writer.writerow([
                update.title,
                update.content,
                update.date,
                update.created_by.username if update.created_by else '',
            ])
        return response

    download_updates_csv.short_description = "Download selected updates as CSV"


# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'update', 'booked_at')  # Display user, update, and booking date
    search_fields = ('user__username', 'update__title')  # Search by user or update title
    list_filter = ('booked_at', 'update')  # Filter by booking date and update


# FinancialAccount Admin
@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'phone_number')


# Withdrawal Admin
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'phone_number', 'status', 'requested_at', 'processed_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'phone_number')