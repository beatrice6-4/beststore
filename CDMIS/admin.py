from django.contrib import admin
from .models import Group, Payment, Activity, Training, Service, Finance
from django.http import HttpResponse
import csv

admin.site.register(Group)
admin.site.register(Activity)
admin.site.register(Training)
admin.site.register(Service)
admin.site.register(Finance)

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