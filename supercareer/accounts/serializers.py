from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, UserProfile, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)
    specialization = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'full_name',
                  'skills', 'hourly_rate', 'specialization', 
                  'experience', 'bio', 'education', 'preferences']

    def create(self, validated_data):
        # Extract full_name and split it
        full_name = validated_data.pop('full_name', '')
        if full_name:
            parts = full_name.split(' ', 1)
            validated_data['first_name'] = parts[part_idx] if (part_idx := 0) < len(parts) else ''
            validated_data['last_name'] = parts[1] if len(parts) > 1 else ''
        
        # Extract profile data
        skills_data = validated_data.pop('skills', [])
        profile_fields = ['hourly_rate', 'specialization', 
                          'experience', 'bio', 'education', 'preferences']
        profile_data = {field: validated_data.pop(field) for field in profile_fields if field in validated_data}
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create profile
        profile = UserProfile.objects.create(user=user, **profile_data)
        
        # Handle skills
        for skill_name in skills_data:
            skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
            profile.skills.add(skill)
        
        return user


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    skills = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Skill.objects.all(),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'username', 
                  'bio', 'specialization', 'experience', 'hourly_rate', 
                  'education', 'preferences', 'skills', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Handle User model fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Handle skills separately if provided as strings/slugs
        skills_data = validated_data.pop('skills', None)
        if skills_data is not None:
            instance.skills.clear()
            for skill_name in skills_data:
                # Skill is already a Skill object because of queryset=Skill.objects.all()
                instance.skills.add(skill_name)

        # Handle other profile fields
        return super().update(instance, validated_data)



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        # SimpleJWT expects username by default, we map email to username field
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                # Set username in attrs for parent class
                attrs[self.username_field] = email
                attrs['password'] = password
            else:
                raise serializers.ValidationError('Invalid email or password.')
        
        data = super().validate(attrs)

        # Add user data to the response
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data

        # Add profile data to the response
        try:
            profile = UserProfile.objects.get(user=self.user)
            profile_serializer = ProfileSerializer(profile)
            data['profile'] = profile_serializer.data
        except UserProfile.DoesNotExist:
            data['profile'] = None

        return data
