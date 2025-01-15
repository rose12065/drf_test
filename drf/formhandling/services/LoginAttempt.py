from datetime import timedelta
from django.utils.timezone import now
from ..models import LoginAttempt

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
