from django.contrib import admin
from .models import Group, Payment, Activity, Training, Service

admin.site.register(Group)
admin.site.register(Payment)
admin.site.register(Activity)
admin.site.register(Training)
admin.site.register(Service)