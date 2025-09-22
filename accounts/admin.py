from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, ContactMessage
from django.utils.html import format_html


# Register your models here.



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
