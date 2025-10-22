from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Withdrawal

@receiver(post_save, sender=Withdrawal)
def notify_user_on_withdrawal(sender, instance, created, **kwargs):
    if created:
        # Notify the user when a withdrawal is created
        subject = "Withdrawal Request Submitted"
        message = f"""
        Dear {instance.user.username},

        Your withdrawal request for {instance.amount} has been submitted successfully.

        Details:
        - Amount: {instance.amount}
        - Phone Number: {instance.phone_number}
        - Status: {instance.status}
        - Requested At: {instance.requested_at}

        Thank you,
        CDMIS Management
        """
    else:
        # Notify the user when the status changes
        subject = f"Withdrawal Status Update: {instance.status}"
        message = f"""
        Dear {instance.user.username},

        Your withdrawal request for {instance.amount} has been {instance.status.lower()}.

        Details:
        - Amount: {instance.amount}
        - Phone Number: {instance.phone_number}
        - Status: {instance.status}
        - Processed At: {instance.processed_at or 'N/A'}

        Thank you,
        CDMIS Management
        """

    recipient_email = instance.user.email

    # Send the email
    send_mail(
        subject,
        message,
        'mamamaassaibakers@gmail.com',  # Replace with your sender email
        [recipient_email],
        fail_silently=False,
    )