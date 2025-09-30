from django.db import models

# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    registration_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.group.name} - {self.amount}"

class Activity(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=100)
    activity_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.group.name})"

class Training(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='trainings')
    topic = models.CharField(max_length=100)
    trainer = models.CharField(max_length=100)
    training_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.topic} ({self.group.name})"

class Service(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    service_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.group.name})"
    
from django.db import models
from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='cdmis_orders')
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"