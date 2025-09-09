from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json

from store.models import Product
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage

from django.template.loader import render_to_string

@login_required(login_url='login')
def payments(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        # Store transaction details inside Payment model
        payment = Payment(
            user = request.user,
            payment_id = body.get('transID', ''),
            payment_method = body.get('payment_method', ''),
            amount_paid = order.order_total,
            status = body.get('status', ''),
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order received email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Send order number and transaction id back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    else:
        # For GET requests, do not try to parse JSON
        return redirect('home')