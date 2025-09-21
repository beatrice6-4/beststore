from django.contrib import admin
from django import forms
from .models import Payment, Order, OrderProduct

class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        reference_code = cleaned_data.get('reference_code')
        payment_id = cleaned_data.get('payment_id')
        self._order = None
        if not payment_id:
            raise forms.ValidationError("Mpesa code (payment_id) is required.")
        if reference_code:
            try:
                order = Order.objects.get(order_number=reference_code)
                self._order = order
            except Order.DoesNotExist:
                raise forms.ValidationError("No order found with this reference code.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, '_order') and self._order:
            instance.user = self._order.user
            instance.amount_paid = self._order.order_total
            instance.payment_method = 'Mpesa'
            instance.status = 'Paid Via Mpesa'
            instance.payment_id = self.cleaned_data.get('payment_id')
            if commit:
                instance.save()  # Save Payment first!
                # Now link payment to order and update order status
                self._order.payment = instance
                self._order.status = "Completed"
                self._order.is_ordered = True
                self._order.save()
        else:
            if commit:
                instance.save()
        return instance
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ('user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    search_fields = ('user__email', 'payment_id', 'payment_method', 'reference_code')
    list_filter = ('status', 'payment_method', 'created_at')
    readonly_fields = ('user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)