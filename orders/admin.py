from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    readonly_fields = ('payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at', 'get_payments']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline, PaymentInline]

    def get_payments(self, obj):
        payments = Payment.objects.filter(order=obj)
        if payments.exists():
            return ", ".join([f"{p.payment_method} ({p.amount_paid})" for p in payments])
        return "No Payment"
    get_payments.short_description = "Payments"

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)