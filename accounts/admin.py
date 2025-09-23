from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, ContactMessage
from django.utils.html import format_html
from .models import Transaction  # Adjust import if Transaction is in another app



# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'order__user__email')

admin.site.register(Transaction, TransactionAdmin)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'message')

admin.site.register(ContactMessage, ContactMessageAdmin)

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
