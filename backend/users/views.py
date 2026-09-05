from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .models import OfficerProfile
from .serializers import OfficerLoginSerializer, OfficerProfileSerializer
from .permissions import IsOfficerActive

class HealthCheckView(APIView):
    """
    Public health check endpoint for monitoring API and system status.
    Expected response per specification:
    {
        "status": "ok",
        "message": "Legal Metrology API is running"
    }
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "message": "Legal Metrology API is running"
            },
            status=status.HTTP_200_OK
        )

class OfficerLoginView(APIView):
    """
    Officer Login endpoint:
    Accepts Officer ID and password.
    Returns auth token and officer profile details.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OfficerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            profile = serializer.validated_data['profile']

            # Get or generate DRF authentication token
            token, _ = Token.objects.get_or_create(user=user)
            officer_data = OfficerProfileSerializer(profile).data

            return Response(
                {
                    "success": True,
                    "status": "success",
                    "message": "Login successful",
                    "token": token.key,
                    "user": officer_data,
                    "officer": officer_data
                },
                status=status.HTTP_200_OK
            )

        errors = serializer.errors
        error_msg = "Invalid Officer ID or password."
        if 'non_field_errors' in errors:
            error_msg = str(errors['non_field_errors'][0])
        elif 'officer_id' in errors and 'password' not in errors:
            error_msg = "Please enter a valid Officer ID."
        elif 'password' in errors and 'officer_id' not in errors:
            error_msg = "Please enter your password."

        return Response(
            {
                "success": False,
                "status": "error",
                "message": error_msg,
            },
            status=(
                status.HTTP_401_UNAUTHORIZED
                if 'non_field_errors' in errors
                else status.HTTP_400_BAD_REQUEST
            )
        )

class OfficerProfileView(APIView):
    """
    Retrieves the currently authenticated officer's profile information.
    Protected endpoint: requires valid Token and active status.
    """
    permission_classes = [permissions.IsAuthenticated, IsOfficerActive]

    def get(self, request):
        try:
            profile = request.user.officer_profile
            data = OfficerProfileSerializer(profile).data
            # Response includes user and officer keys as well as root-level fields
            return Response(
                {
                    "success": True,
                    "status": "success",
                    "user": data,
                    "officer": data,
                    **data
                },
                status=status.HTTP_200_OK
            )
        except OfficerProfile.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "status": "error",
                    "message": "No officer profile associated with this user."
                },
                status=status.HTTP_404_NOT_FOUND
            )

class OfficerLogoutView(APIView):
    """
    Invalidates current session token.
    Protected endpoint: requires valid Token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete token to log out
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass

        return Response(
            {
                "success": True,
                "status": "ok",
                "message": "Officer successfully logged out."
            },
            status=status.HTTP_200_OK
        )
