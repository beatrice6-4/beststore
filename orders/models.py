from datetime import datetime
from django.db import models
from accounts.models import Account
from orders.generateAcesstoken import get_access_token
from store.models import Product, Variation
import requests
import base64
import random
import string

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    reference_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id if self.payment_id else "No Code"

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='orders')
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='Accepted')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return f'Order {self.order_number} by {self.full_name()}'
    






    def initiate_mpesa_stkpush(self, phone_number):
        access_token = get_access_token()
        if not access_token:
            return {'error': 'Access token not found.'}

        # Format phone number
        if phone_number.startswith("+"):
            phone_number = phone_number[1:]
        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]
        if not phone_number.startswith("254") or len(phone_number) != 12:
            return {'error': 'Invalid phone number format. Use 2547XXXXXXXX.'}

        business_short_code = '3581517'  # LIVE shortcode
        passkey = "46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933"  # LIVE passkey
        process_request_url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'https://mamamaasaibakers.com/orders/mpesa/callback/'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        transaction_desc = f'Payment for Order {self.order_number}'

        # Generate AccountReference: 4 random capital letters + 4 random digits
        random_letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        random_digits = ''.join(random.choices(string.digits, k=4))
        account_reference = f'{random_letters}{random_digits}'

        amount = int(self.order_total)

        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

        stk_push_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': 'Failed to initiate STK Push.', 'details': str(e)}





class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name='order_products')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.product_name} (Order {self.order.order_number})'