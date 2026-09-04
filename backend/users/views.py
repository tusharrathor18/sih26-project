from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .models import OfficerProfile
from .serializers import OfficerLoginSerializer, OfficerProfileSerializer

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

            return Response(
                {
                    "status": "success",
                    "message": "Officer authentication successful",
                    "token": token.key,
                    "officer": OfficerProfileSerializer(profile).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "error",
                "message": "Authentication failed",
                "errors": serializer.errors
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

class OfficerProfileView(APIView):
    """
    Retrieves the currently authenticated officer's profile information.
    Protected endpoint: requires valid Token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.officer_profile
            return Response(
                {
                    "status": "success",
                    "officer": OfficerProfileSerializer(profile).data
                },
                status=status.HTTP_200_OK
            )
        except OfficerProfile.DoesNotExist:
            return Response(
                {
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
                "status": "ok",
                "message": "Officer successfully logged out."
            },
            status=status.HTTP_200_OK
        )
