from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_total_price')
    fields = ('product', 'quantity', 'price', 'get_total_price')

    def get_total_price(self, obj):
        """Calculate total price for each order item"""
        if obj and obj.price is not None and obj.quantity is not None:
            return f"KES {obj.price * obj.quantity:,.2f}"
        return "KES 0.00"
    get_total_price.short_description = 'Total Price'

@admin.register(Order)  # Use the decorator to register the model
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model"""

    list_display = (
        'order_id',
        'customer_name',
        'email',
        'phone',
        'total_amount_display',
        'status_badge',
        'payment_method',
        'created_at'
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'id'
    )

    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'total_items',
        'order_summary'
    )

    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'status', 'payment_method', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'user')
        }),
        ('Delivery Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'country')
        }),
        ('Order Details', {
            'fields': ('order_summary', 'total_items', 'order_note'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_pending', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def order_id(self, obj):
        """Display order ID with a hash"""
        return f"#{obj.pk}"
    order_id.short_description = 'Order ID'

    def customer_name(self, obj):
        """Display full customer name"""
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = 'Customer Name'

    def total_amount_display(self, obj):
        """Display total amount in a formatted way"""
        return f"KES {obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'

    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#FFA500',
            'processing': '#0099FF',
            'shipped': '#9933FF',
            'delivered': '#00CC00',
            'cancelled': '#FF0000',
            'completed': '#00CC00',
        }
        color = colors.get(obj.status, '#808080')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 3px;">{obj.get_status_display()}</span>'
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True

    def total_items(self, obj):
        """Display total number of items in the order"""
        count = obj.items.count()
        return count if count else 0
    total_items.short_description = 'Total Items'

    def order_summary(self, obj):
        """Display a summary of order items"""
        items = obj.items.all()
        if not items.exists():
            return "No items in this order"

        summary = "<ul style='margin: 10px 0;'>"
        for item in items:
            summary += f"<li>{item.product.product_name} x {item.quantity} - KES {item.get_total_price():,.2f}</li>"
        summary += "</ul>"
        return summary
    order_summary.short_description = 'Order Items'
    order_summary.allow_tags = True

    # Actions
    def mark_pending(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} order(s) marked as Pending.')
    mark_pending.short_description = 'Mark selected as Pending'

    def mark_processing(self, request, queryset):
        count = queryset.update(status='processing')
        self.message_user(request, f'{count} order(s) marked as Processing.')
    mark_processing.short_description = 'Mark selected as Processing'

    def mark_shipped(self, request, queryset):
        count = queryset.update(status='shipped')
        self.message_user(request, f'{count} order(s) marked as Shipped.')
    mark_shipped.short_description = 'Mark selected as Shipped'

    def mark_delivered(self, request, queryset):
        count = queryset.update(status='delivered')
        self.message_user(request, f'{count} order(s) marked as Delivered.')
    mark_delivered.short_description = 'Mark selected as Delivered'

    def mark_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'{count} order(s) marked as Cancelled.')
    mark_cancelled.short_description = 'Mark selected as Cancelled'

    def has_delete_permission(self, request, obj=None):
        """
        Allow deletion only for superusers.
        The `obj` argument represents the object being edited (can be None).
        """
        return request.user.is_superuser