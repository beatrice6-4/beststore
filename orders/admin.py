from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    search_fields = ('user__email', 'payment_id', 'payment_method')
    list_filter = ('status', 'payment_method', 'created_at')
    readonly_fields = ('user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    # Payments are recorded via callback, so fields are read-only

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)