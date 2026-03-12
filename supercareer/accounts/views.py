from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializers import RegisterSerializer, ProfileSerializer, CustomTokenObtainPairSerializer, UserSerializer
from .models import User, UserProfile


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Return the created data including profile info and tokens
            response_data = {
                "message": "User and Profile created successfully",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": UserSerializer(user).data,
                "profile": ProfileSerializer(user.profile).data
            }
            return Response(response_data, status=201)

        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Handle either 'refresh' or 'token' key for flexibility
            refresh_token = request.data.get("refresh") or request.data.get("token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except (TokenError, KeyError):
            return Response({"error": "Invalid token or token missing"}, status=400)


class GoogleAuthView(APIView):
    """Authenticate/register users using a Google OAuth2 ID token."""

    def post(self, request):
        id_token_str = request.data.get('id_token') or request.data.get('token')
        if not id_token_str:
            return Response({'error': 'id_token is required'}, status=400)

        if not settings.GOOGLE_CLIENT_ID:
            return Response(
                {'error': 'GOOGLE_CLIENT_ID is not configured on the server environment.'},
                status=500,
            )

        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=400)

        email = id_info.get('email')
        if not email:
            return Response({'error': 'Google token did not contain an email'}, status=400)

        first_name = id_info.get('given_name') or ''
        last_name = id_info.get('family_name') or ''
        full_name = id_info.get('name', '')
        if not (first_name or last_name) and full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        # Create or get user
        user = User.objects.filter(email=email).first()
        if not user:
            username_base = email.split('@')[0]
            username = f"{username_base}_{get_random_string(6)}"
            role = request.data.get('role', 'job_seeker')
            user = User.objects.create_user(
                email=email,
                username=username,
                role=role,
                first_name=first_name,
                last_name=last_name,
                password=None,
            )
            user.set_unusable_password()
            user.save()

        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)

        # Issue tokens
        refresh = RefreshToken.for_user(user)
        response_data = {
            'message': 'Logged in with Google successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(user.profile).data,
        }
        return Response(response_data, status=200)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = UserProfile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
