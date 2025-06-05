import random

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.core.mail import send_mail


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email_verified)
        )

email_verification_token = EmailVerificationTokenGenerator()

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    subject = "Tasdiqlash kodingiz"
    message = f"Ro'yxatdan o'tishni tasdiqlash uchun quyidagi kodni kiriting: {code}"
    send_mail(subject, message, 'your_email@example.com', [email])