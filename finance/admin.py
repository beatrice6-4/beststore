from django.contrib import admin
from .models import FinanceRecord

@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment', 'user', 'recorded_at')
    search_fields = ('order__order_number', 'payment__payment_id', 'user__email')
    list_filter = ('recorded_at',)