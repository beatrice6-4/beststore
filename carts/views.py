from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    """Generate a unique cart ID for the session."""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the session ID
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    # Check if the product already exists in the cart
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if not created:
        cart_item.quantity += 1  # Increment the quantity if it already exists
    cart_item.save()

    return redirect('cart:cart')


def remove_cart(request, product_id, cart_item_id):
    """Remove a product from the cart."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product_id=product_id, id=cart_item_id, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  # Decrease the quantity
            cart_item.save()
        else:
            cart_item.delete()  # Remove the item if quantity is 1
    except ObjectDoesNotExist:
        pass
    return redirect('cart:cart')


def remove_cart_item(request, product_id, cart_item_id):
    """Remove a cart item completely."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product_id=product_id, id=cart_item_id, cart=cart)
        cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('cart:cart')


def cart(request):
    """Display the cart page."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = sum(item.product.price * item.quantity for item in cart_items)
        quantity = sum(item.quantity for item in cart_items)
    except ObjectDoesNotExist:
        cart_items = []
        total = 0
        quantity = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
    }
    return render(request, 'carts/cart.html', context)


def checkout(request):
    """Display the checkout page."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = sum(item.product.price * item.quantity for item in cart_items)
        quantity = sum(item.quantity for item in cart_items)
    except ObjectDoesNotExist:
        cart_items = []
        total = 0
        quantity = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
    }
    return render(request, 'carts/checkout.html', context)