# myapp/services/alert_service.py

from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client


class AlertService:
    def send_email(self, subject, message, recipient_email):
        try:
            send_mail(
                subject,
                message,
                'greenmart893@gmail.com',  # Replace with your email
                [recipient_email],
                fail_silently=False,
            )
            return True, "Email sent successfully!"
        except Exception as e:
            return False, f"Email sending failed: {str(e)}"

    def send_sms(self, phone_number, message):
        # try:
            # Twilio or other SMS service logic
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            response = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to= phone_number,
            )
            return True, "SMS sent successfully"
        # except Exception as e:
            return False, str(e)
