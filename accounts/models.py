from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
        user.is_administrator = True
        user.is_active = True
        user.is_finance = True
        user.is_staff = True
        user.is_superadmin = True
        user.role = Account.Role.ADMINISTRATOR  # Set superuser as administrator
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMINISTRATOR = 'administrator', 'Administrator'
        FINANCE = 'finance', 'Finance'
        NORMAL = 'normal', 'Normal User'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NORMAL,
        help_text="User role. Default is Normal User."
    )



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
    
   