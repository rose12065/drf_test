from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_reminder_email(email, subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return f"Email sent to {email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
