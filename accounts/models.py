from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, DecimalValidator
import uuid
import logging

logger = logging.getLogger(__name__)

# ============ CUSTOM USER MANAGER ============
class MyAccountManager(BaseUserManager):
    """Custom manager for Account model"""
    
    def create_user(self, first_name, last_name, username, email, password=None):
        """Create and save a regular user"""
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
        """Create and save a superuser"""
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
    """Custom user model with extended functionality"""
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('finance', 'Finance'),
        ('user', 'User'),
        ('trader', 'Trader'),
    )
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        help_text='User role for system permissions'
    )
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    is_superadmin = models.BooleanField(default=False)
    
    # Trading fields
    deriv_token = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Deriv API token'
    )
    deriv_connected = models.BooleanField(
        default=False,
        help_text='Whether user has connected Deriv account'
    )
    
    # Timestamp fields with proper defaults
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Account creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last account update timestamp'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]

    def full_name(self):
        """Return full name"""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_full_name(self):
        """Get full name (Django convention)"""
        return self.full_name()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Check permission"""
        return self.is_admin or self.is_superuser

    def has_module_perms(self, add_label):
        """Check module permissions"""
        return True

    def is_administrator(self):
        """Check if user is admin"""
        return self.role == 'admin' or self.is_superuser

    def is_finance(self):
        """Check if user is finance"""
        return self.role == 'finance'

    def is_normal_user(self):
        """Check if user is normal user"""
        return self.role == 'user'

    def is_trader(self):
        """Check if user is trader"""
        return self.role == 'trader'


# ============ CONTACT MESSAGE MODEL ============
class ContactMessage(models.Model):
    """Contact form submissions from website visitors"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Message submission time'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.email}"


# ============ TRANSACTION MODEL ============
class Transaction(models.Model):
    """Financial transaction history"""
    
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Transaction creation time'
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Transaction completion time'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

    def clean(self):
        """Validate transaction data"""
        if self.amount < 0:
            raise models.ValidationError('Amount cannot be negative')


# ============ WISHLIST MODEL ============
class Wishlist(models.Model):
    """User wishlist for products"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wishlist_items'
    )
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When item was added to wishlist'
    )

    class Meta:
        ordering = ['-added_at']
        unique_together = ('user', 'product_id')
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        indexes = [
            models.Index(fields=['user', 'product_id']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product_name}"


# ============ TRADE HISTORY MODEL ============
class TradeHistory(models.Model):
    """Trading history from Deriv platform"""
    
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='trades'
    )
    symbol = models.CharField(max_length=20)
    contract_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='CALL')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    duration = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    entry_price = models.DecimalField(
        max_digits=10, 
        decimal_places=5, 
        null=True, 
        blank=True
    )
    exit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=5, 
        null=True, 
        blank=True
    )
    profit_loss = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    profit_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    contract_id = models.CharField(max_length=50, blank=True, null=True)
    trade_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Trade creation time'
    )
    opened_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When trade was opened'
    )
    closed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When trade was closed'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update time'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trade History'
        verbose_name_plural = 'Trade Histories'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['symbol']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.symbol} {self.contract_type}"

    def save(self, *args, **kwargs):
        """Override save to ensure valid datetime values"""
        # Ensure opened_at is set to a valid datetime
        if self.opened_at == "UNKNOWN" or (isinstance(self.opened_at, str) and self.opened_at):
            self.opened_at = timezone.now()
        
        # Ensure closed_at is set properly
        if self.closed_at == "UNKNOWN" or (isinstance(self.closed_at, str) and self.closed_at):
            self.closed_at = None
        
        super().save(*args, **kwargs)

    @property
    def return_on_investment(self):
        """Calculate return on investment percentage"""
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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='trading_profile'
    )
    
    # Trading statistics
    total_trades = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    winning_trades = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    losing_trades = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_amount_traded = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_profit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    total_loss = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Account balance
    account_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    daily_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Preferences
    notification_email = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    is_professional = models.BooleanField(default=False)
    account_level = models.CharField(
        max_length=20, 
        choices=ACCOUNT_LEVEL_CHOICES, 
        default='beginner'
    )
    
    # Timestamps with proper defaults
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Profile creation time'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last profile update time'
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['account_level']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - Trading Profile"

    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        total = self.winning_trades + self.losing_trades
        return (self.winning_trades / total) * 100 if total > 0 else 0

    @property
    def average_trade_size(self):
        """Calculate average trade size"""
        return self.total_amount_traded / self.total_trades if self.total_trades > 0 else 0

    @property
    def profit_factor(self):
        """Calculate profit factor"""
        if self.total_loss > 0:
            return self.total_profit / self.total_loss
        elif self.total_profit > 0:
            return float('inf')
        else:
            return 0


# ============ ADMIN LOG MODEL ============
class AdminLog(models.Model):
    """Admin activity audit trail"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='admin_logs'
    )
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Log creation time'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
        indexes = [
            models.Index(fields=['admin_user', 'created_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        admin_name = self.admin_user.username if self.admin_user else 'Unknown'
        return f"{admin_name} - {self.action}"


# ============ CATEGORY MODEL ============
class Category(models.Model):
    """Product or service categories"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Category creation time'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last category update time'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ============ SIGNALS ============
@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when Account is created"""
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
            logger.info(f"UserProfile created for {instance.email}")
        except Exception as e:
            logger.error(f"Error creating UserProfile for {instance.email}: {str(e)}")

@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when Account is saved"""
    try:
        if hasattr(instance, 'trading_profile'):
            instance.trading_profile.save()
    except Exception as e:
        logger.error(f"Error saving UserProfile for {instance.email}: {str(e)}")