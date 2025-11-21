from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Account, ContactMessage, Transaction,
    UserProfile, Wishlist, AdminLog, Category
)

# ============ CATEGORY ADMIN ============
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'id')
        }),
        ('Details', {
            'fields': ('description', 'image', 'icon')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============ ACCOUNT ADMIN ============
@admin.register(Account)
class AccountAdmin(UserAdmin):
    """Custom admin for Account model"""
    list_display = ['email', 'username', 'get_full_name', 'role', 'created_at']
    list_filter = ['is_active', 'role', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at', 'date_joined', 'last_login']

    fieldsets = (
        ('Login', {'fields': ('email', 'username', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'is_superadmin')}),
        ('Dates', {'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


# ============ CONTACT MESSAGE ADMIN ============
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin for ContactMessage"""
    list_display = ['subject', 'email', 'name', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['id', 'created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    fieldsets = (
        ('Message Info', {
            'fields': ('id', 'name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} message(s) marked as read.')
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f'{count} message(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected as unread"

    def has_add_permission(self, request):
        return False





# ============ WISHLIST ADMIN ============
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for Wishlist"""
    list_display = ['get_user', 'product_name', 'product_id', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'product_name', 'product_id']
    readonly_fields = ['id', 'added_at']

    fieldsets = (
        ('User & Product', {
            'fields': ('user', 'id', 'product_id', 'product_name')
        }),
        ('Timestamp', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )

    def get_user(self, obj):
        return obj.user.email
    get_user.short_description = 'User Email'




# ============ USER PROFILE ADMIN ============
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile"""
    list_display = ['get_user', 'total_trades', 'get_win_rate', 'total_profit', 'account_level']
    list_filter = ['account_level', 'is_professional', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('User Info', {
            'fields': ('user', 'id')
        }),
        ('Trading Statistics', {
            'fields': ('total_trades', 'winning_trades', 'losing_trades', 'total_amount_traded')
        }),
        ('Profitability', {
            'fields': ('total_profit', 'total_loss')
        }),
        ('Account Info', {
            'fields': ('account_balance', 'daily_balance', 'account_level', 'is_professional')
        }),
        ('Settings', {
            'fields': ('notification_email', 'two_factor_enabled'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_user(self, obj):
        return obj.user.email
    get_user.short_description = 'User Email'

    def get_win_rate(self, obj):
        return f"{obj.win_rate:.2f}%"
    get_win_rate.short_description = 'Win Rate'


# ============ ADMIN LOG ADMIN ============
@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    """Admin for AdminLog"""
    list_display = ['get_admin', 'action', 'model_name', 'ip_address', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['admin_user__email', 'action', 'model_name']
    readonly_fields = ['id', 'created_at']

    fieldsets = (
        ('Admin Info', {
            'fields': ('admin_user', 'id')
        }),
        ('Action Details', {
            'fields': ('action', 'model_name', 'object_id')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_admin(self, obj):
        return obj.admin_user.email if obj.admin_user else 'Unknown'
    get_admin.short_description = 'Admin User'