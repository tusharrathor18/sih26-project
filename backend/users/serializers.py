from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import OfficerProfile

class OfficerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for exposing officer profile details to frontend and API callers.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OfficerProfile
        fields = [
            'id',
            'officer_id',
            'name',
            'email',
            'username',
            'designation',
            'department',
            'jurisdiction',
            'role',
            'phone',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'officer_id', 'created_at']

class OfficerLoginSerializer(serializers.Serializer):
    """
    Serializer to authenticate Legal Metrology officers using Officer ID and password.
    Enforces strict business rules:
      - Officer ID must exist in pre-registered records (no public registration).
      - Officer account must be active.
      - Password must be verified securely via Django auth.
      - Safe error messaging to mitigate enumeration vulnerabilities.
    """
    officer_id = serializers.CharField(
        required=True,
        trim_whitespace=True,
        error_messages={'blank': 'Please enter your Officer ID.'}
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={'blank': 'Please enter your password.'}
    )

    def validate(self, attrs):
        officer_id = attrs.get('officer_id')
        password = attrs.get('password')

        # 1. Lookup officer profile
        try:
            profile = OfficerProfile.objects.select_related('user').get(officer_id=officer_id)
        except OfficerProfile.DoesNotExist:
            raise serializers.ValidationError({
                'officer_id': 'Officer account not found / invalid credentials.',
                'non_field_errors': 'Invalid Officer ID or password.'
            })

        # 2. Check if officer profile or associated user is active
        if not profile.is_active or not profile.user.is_active:
            raise serializers.ValidationError({
                'non_field_errors': 'Officer account is inactive. Please contact the Department Administrator.'
            })

        # 3. Secure password verification
        user = authenticate(username=profile.user.username, password=password)
        if not user:
            raise serializers.ValidationError({
                'non_field_errors': 'Invalid Officer ID or password.'
            })

        attrs['user'] = user
        attrs['profile'] = profile
        return attrs
