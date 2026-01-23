#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beststore.settings')
django.setup()

from django.contrib.auth.models import User

# Create or update admin user
admin_user, created = User.objects.get_or_create(username='admin')
admin_user.email = 'admin@beststore.com'
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.set_password('admin123')
admin_user.save()

if created:
    print("✓ Superuser 'admin' created successfully")
else:
    print("✓ Superuser 'admin' password updated")
    
print(f"\nLogin credentials:")
print(f"  Username: admin")
print(f"  Password: admin123")
print(f"  URL: http://127.0.0.1:8000/admin/")
