from django.contrib.auth.hashers import check_password
from ..models import CustomUser
from .LoginAttempt import LoginAttemptService
from .Emailservice import EmailService

class UserValidationService:
    @staticmethod
    def validate_user(email, password):
        # Check if user exists
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise ValueError("Invalid user.")

        # Check if user is locked out
        if LoginAttemptService.is_locked_out(user):
            raise ValueError("Too many failed attempts. Please try again later.")

        # Check password
        if not check_password(password, user.password):
            LoginAttemptService.increment_attempts(user)
            if LoginAttemptService.is_locked_out(user):
                EmailService.send_login_warning(email)
            raise ValueError("Invalid email or password.")

        # Reset attempts on successful login
        LoginAttemptService.reset_attempts(user)
        return user
