from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# ============ CUSTOM USER MANAGER ============
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
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
        user.is_superuser = True
        user.role = 'admin'
        user.save(using=self._db)
        return user


# ============ ACCOUNT MODEL ============
class Account(AbstractUser):
    """Custom user model"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('finance', 'Finance'),
        ('user', 'User'),
        ('trader', 'Trader'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    is_superadmin = models.BooleanField(default=False)
    
    # Trading fields
    deriv_token = models.CharField(max_length=255, blank=True, null=True)
    deriv_connected = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return self.full_name()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_superuser

    def has_module_perms(self, add_label):
        return True

    def is_administrator(self):
        return self.role == 'admin' or self.is_superuser

    def is_finance(self):
        return self.role == 'finance'

    def is_normal_user(self):
        return self.role == 'user'

    def is_trader(self):
        return self.role == 'trader'


# ============ CONTACT MESSAGE MODEL ============
class ContactMessage(models.Model):
    """Contact form submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.subject} - {self.email}"


# ============ TRANSACTION MODEL ============
class Transaction(models.Model):
    """Transaction history"""
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('trade', 'Trade'),
        ('refund', 'Refund'),
        ('payment', 'Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


# ============ WISHLIST MODEL ============
class Wishlist(models.Model):
    """User wishlist"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ('user', 'product_id')

    def __str__(self):
        return f"{self.user.email} - {self.product_name}"


# ============ TRADE HISTORY MODEL ============
class TradeHistory(models.Model):
    """Trading history from Deriv"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
        ('expired', 'Expired'),
    ]
    
    TRADE_TYPE_CHOICES = [
        ('CALL', 'Call (Up)'),
        ('PUT', 'Put (Down)'),
        ('TOUCH', 'Touch'),
        ('NO_TOUCH', 'No Touch'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=20)
    contract_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='CALL')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    entry_price = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    exit_price = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    contract_id = models.CharField(max_length=50, blank=True, null=True)
    trade_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trade Histories'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.symbol} {self.contract_type}"

    @property
    def return_on_investment(self):
        if self.amount and self.profit_loss:
            return (self.profit_loss / self.amount) * 100
        return 0


# ============ USER PROFILE MODEL ============
class UserProfile(models.Model):
    """Extended user profile with trading statistics"""
    ACCOUNT_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trading_profile')
    
    # Trading statistics
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    total_amount_traded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Account balance
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Preferences
    notification_email = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    is_professional = models.BooleanField(default=False)
    account_level = models.CharField(max_length=20, choices=ACCOUNT_LEVEL_CHOICES, default='beginner')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - Trading Profile"

    @property
    def win_rate(self):
        total = self.winning_trades + self.losing_trades
        return (self.winning_trades / total) * 100 if total > 0 else 0

    @property
    def average_trade_size(self):
        return self.total_amount_traded / self.total_trades if self.total_trades > 0 else 0

    @property
    def profit_factor(self):
        return self.total_profit / self.total_loss if self.total_loss > 0 else (float('inf') if self.total_profit > 0 else 0)


# ============ ADMIN LOG MODEL ============
class AdminLog(models.Model):
    """Admin activity audit trail"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Admin Logs'

    def __str__(self):
        return f"{self.admin_user.username if self.admin_user else 'Unknown'} - {self.action}"


# ============ SIGNALS ============
@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when Account is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)




# Add this to the end of accounts/models.py

class Category(models.Model):
    """Product or service categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name