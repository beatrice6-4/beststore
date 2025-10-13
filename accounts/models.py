from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            # role will default to 'normal' automatically
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.role = Account.Role.ADMINISTRATOR  # Set superuser as administrator
        user.save(using=self._db)
        return user

# accounts/models.py
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('finance', 'Finance'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)




    def is_administrator(self):
        """General roles for administrator."""
        return self.role == self.Role.ADMINISTRATOR

    def is_finance(self):
        """Specific roles for finance."""
        return self.role == self.Role.FINANCE

    def is_normal_user(self):
        """Normal roles for normal user."""
        return self.role == self.Role.NORMAL

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    

from django.db import models
from django.conf import settings

class ContactMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=40)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.subject} from {self.user.email}"
    

from django.db import models
from orders.models import Order

class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
    

from django.db import models
from django.conf import settings
from store.models import Product

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name}"
    


from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.category_name


from django.db import models
from accounts.models import Account

class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='created_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.description}"