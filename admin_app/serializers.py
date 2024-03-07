from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from django.contrib.auth import authenticate
from accounts.serializers import LoginSerializer


class DashboardSerializer(serializers.Serializer):
    """
-    Serializer for providing dashboard statistics.
-
-    This serializer includes fields for total jobs, total coders, total clients,
-    and total revenue. The data is calculated based on specific business logic
-    defined in the `calculate_totals` method.
-
-    Attributes:
-        total_jobs (int): The total number of jobs.
-        total_coders (int): The total number of users with the role 'CODER'.
-        total_clients (int): The total number of users with the role 'CLIENT'.
-        total_revenue (int): The total revenue.
-
-    Methods:
-        calculate_totals(): Method to calculate and return statistics.
-    """
    total_jobs = serializers.IntegerField(read_only=True)
    total_coders = serializers.IntegerField(read_only=True)
    total_clients = serializers.IntegerField(read_only=True)
    total_revenue = serializers.IntegerField(read_only=True)
    
    class Meta:
        fields = ['total_jobs', 'total_coders', 'total_clients', 'total_revenue']

    def calculate_totals(self):
        """
-        Calculate statistics for the dashboard.
-        The method retrieves the total number of jobs, total number of coders,
-        total number of clients, and total revenue based on specific business logic.
-        Returns:
-            dict: A dictionary containing the calculated statistics.
-        """
        total_jobs = 1000
        total_coders = User.objects.filter(role='CODER').count()
        total_clients = User.objects.filter(role='CLIENT').count()
        total_revenue = 1000000

        return {
            'total_jobs': total_jobs,
            'total_coders': total_coders,
            'total_clients': total_clients,
            'total_revenue': total_revenue,
        }
        
        
    def to_representation(self, instance):
        """
        Convert the serializer instance into a JSON-compatible representation.

        This method overrides the default behavior of converting the instance
        into a representation suitable for JSON serialization. Here, we customize
        the representation to include statistics data along with pagination metadata.

        Returns:
            dict: A dictionary containing the serialized representation of the instance.
        """
        statistics_data = self.calculate_totals()

        return {
            'count': 1,
            'total_pages': 1,
            'next': None,
            'previous': None,
            'results': [statistics_data],
        }
        

class AdminLoginSerializer(LoginSerializer):
    role = None

    class Meta(LoginSerializer.Meta):
        fields = ["email", "password"]
        read_only_fields = ['role']

    def validate(self, validate_data):
        email = validate_data.get("email")
        password = validate_data.get("password")
        if email and password:
            user = authenticate(
                email=email,
                password=password,
            )
            try:
                registered_user = (User.objects.get(email=email, role__in=['SUPER-ADMIN', 'SUB-ADMIN']))
            except User.DoesNotExist:
                raise AuthenticationFailed(
                    "Unable to log in with provided credentials."
                )
            except:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
            
            if not registered_user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            if user:
                if not user.is_email_verified:
                    raise serializers.ValidationError("Email is not verified.")
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

        else:
            raise serializers.ValidationError(
                "Both email and password are required"
            )  # noqa: 501

        validate_data["access_token"] = access_token
        validate_data["refresh_token"] = refresh_token
        validate_data["user"] = registered_user

        return validate_data

