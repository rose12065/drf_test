from datetime import timedelta
from email.message import EmailMessage

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import now

from .models import CustomUser, LoginAttempt

class LoginAttemptService:
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=15)

    def __init__(self, user):
        self.user = user
        self.login_attempt, _ = LoginAttempt.objects.get_or_create(user=user)

    def is_locked_out(self):
        if not self.login_attempt.lockout_time:
            return False
        return self.login_attempt.lockout_time > now()

    def get_lockout_time_remaining(self):
        if not self.is_locked_out():
            return 0
        return (self.login_attempt.lockout_time - now()).seconds // 60

    def increment_attempts(self):
        self.login_attempt.failed_attempts += 1
        if self.login_attempt.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.login_attempt.lockout_time = now() + self.LOCKOUT_DURATION
        self.login_attempt.save()

    def should_send_warning_email(self):
        return self.login_attempt.failed_attempts == self.MAX_FAILED_ATTEMPTS

    def reset_attempts(self):
        self.login_attempt.failed_attempts = 0
        self.login_attempt.lockout_time = None
        self.login_attempt.save()

class UserValidationService:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.user = None

    def validate(self):
        # Check if user exists
        self.user = CustomUser.objects.filter(email=self.email).first()
        if not self.user:
            raise ValueError("Invalid user.")

        # Initialize LoginAttemptService
        login_service = LoginAttemptService(self.user)

        # Check if user is locked out
        if login_service.is_locked_out():
            raise ValueError(
                f"Too many failed attempts. Please try again in {login_service.get_lockout_time_remaining()} minutes."
            )

        # Check password
        if not check_password(self.password, self.user.password):
            login_service.increment_attempts()

            # Send warning email if max attempts are reached
            if login_service.should_send_warning_email():
                subject = "Suspicious Login Attempt"
                message = (
                    "There have been multiple failed login attempts on your account. "
                    "If this was not you, please secure your account immediately."
                )
                EmailService.send_email(subject, message, [self.email])

            raise ValueError("Invalid email or password.")

        # Reset attempts on successful login
        login_service.reset_attempts()
        return self.user

class EmailService:
    @staticmethod
    def send_email(subject, message, recipient_list, from_email="noreply@example.com"):
        """
        Generalized method to send emails.
        
        Args:
            subject (str): Email subject.
            message (str): Email message.
            recipient_list (list): List of recipient email addresses.
            from_email (str): Sender email address.
        
        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
        
class PasswordResetTokenService:
    def generate_token(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    def validate_token(self, uid, token, user_model):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = user_model.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
            return None

        if not default_token_generator.check_token(user, token):
            return None
        return user
    
class ResetPasswordService:
    def __init__(self, email_service, token_service):
        self.email_service = email_service
        self.token_service = token_service

    def request_password_reset(self, email, user_model):
        user = user_model.objects.filter(email=email).first()
        if not user:
            raise ValueError("User with this email does not exist.")

        # Generate token and send email
        uid, token = self.token_service.generate_token(user)
        reset_url = f"http://localhost:3000/reset-password-token/{uid}/{token}/"
        self.email_service.send_email(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            recipient_list=[email],
        )

    def reset_password(self, uid, token, new_password, user_model):
        user = self.token_service.validate_token(uid, token, user_model)
        if not user:
            raise ValueError("Invalid or expired token.")

        # Reset password
        user.password = make_password(new_password)
        user.save()


