from django.db import models
from store.models import Product, Variation
from accounts.models import Account


class Cart(models.Model):
    """Model representing a shopping cart."""
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    """Model representing an item in the shopping cart."""
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)  # Added default value to avoid IntegrityError
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        """Calculate the subtotal for the cart item."""
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name