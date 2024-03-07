from django.urls import reverse
from rest_framework import serializers
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.models import Site
from urllib.parse import urlparse
from mysite import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes

from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from anymail.exceptions import (
    AnymailUnsupportedFeature,
    AnymailRecipientsRefused,
    AnymailAPIError,
    AnymailInvalidAddress,
    AnymailSerializationError
)


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        try:
            email.send()
        except (AnymailUnsupportedFeature, AnymailRecipientsRefused, AnymailAPIError, AnymailInvalidAddress, AnymailSerializationError) as e:
            if settings.DEBUG:
                print(f"Error occurred during email sending: {e}")
                raise
            return 0
        return 1

    @staticmethod
    def send_verification_email(user):
        token = Util.generate_verification_token(user)
        absurl = f"https://ui-main.hirecoder.info/register?redirecturl=verify-email/token={str(token)}"
        email_body = f"Hi {user.first_name}, please use the link below to verify your email:\n{absurl}"  # noqa:  E501
        data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Verify your email",
            }
        send_status = Util.send_email(data)
        return send_status 

    @staticmethod
    def generate_verification_token(user):
        refresh = RefreshToken.for_user(user)
        return refresh.access_token


class ValidationUtils:
    @staticmethod
    def validate_custom_url(value, domain):
        """
        Validate a URL based on the specified domain.

        Args:
            value (str): The URL to be validated.
            domain (str): The main domain name (e.g., 'youtube').

        Raises:
            serializers.ValidationError: If the provided URL does not match the expected # noqa : E501
            domain patterns.

        Returns:
            str: The validated URL if it meets the specified criteria.
        """
        if value is not None and value.strip():
            parsed_url = urlparse(value)
            netloc_lower = parsed_url.netloc.lower()

            # Check if the netloc matches the domain
            if (
                not netloc_lower.endswith(f".{domain}.com")
                and netloc_lower != f"www.{domain}.com"
                and netloc_lower != f"{domain}.com"
            ):
                raise serializers.ValidationError(
                    f"Please enter a valid '{domain}' url."
                )

        return value


class EmailUtil:
    @staticmethod
    def send_reset_email(user, current_site):
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        absurl = f"https://ui-main.hirecoder.info/password-change?redirecturl=password-reset/{uidb64}/{token}"
        email_body = f"Hi {user.first_name}!,\nClick on the link below to reset your password\n{absurl}"
        data = {
            "email_subject": "Reset your password",
            "email_body": email_body,
            "to_email": user.email,
        }
        return Util.send_email(data)
