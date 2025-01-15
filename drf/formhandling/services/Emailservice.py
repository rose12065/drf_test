from django.core.mail import send_mail

class EmailService:
    @staticmethod
    def send_login_warning(email):
        send_mail(
            subject="Suspicious Login Attempt",
            message="There have been multiple failed login attempts on your account.",
            from_email="noreply@example.com",
            recipient_list=[email],
            fail_silently=False,
        )
