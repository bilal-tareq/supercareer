from rest_framework import serializers
from .models import OTPCode
from accounts.models import User

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            otp_obj = OTPCode.objects.filter(email=email, code=otp, is_verified=False).latest('created_at')
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")
            
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
            
        # Check if OTP was verified
        if not OTPCode.objects.filter(email=data['email'], is_verified=True).exists():
            raise serializers.ValidationError("OTP must be verified before resetting password.")
            
        return data
