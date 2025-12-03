from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),  # Main cart page
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),  # Add product to cart
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),  # Remove product from cart
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),  # Remove cart item
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
]