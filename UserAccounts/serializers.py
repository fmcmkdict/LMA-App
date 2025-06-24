from UserAccounts.models import *
from core.api.serializers import DepartmentSerializers, UnitSerializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# import authenticate for Login serializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model

User = get_user_model()

from core.models import *


class UserSerializer(serializers.ModelSerializer):
    # Nested serializers for related data
    dept = DepartmentSerializers(read_only=True)
    unit = UnitSerializers(read_only=True)
    
    # Computed fields
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'groups', 'last_login']
    
    def get_full_name(self, obj):
        """Return the user's full name"""
        return f"{obj.first_name} {obj.sur_name}"
    
    def get_role(self, obj):
        """Return the user's role based on their permissions"""
        if obj.is_superuser:
            return 'Superuser'
        elif obj.is_hr:
            return 'HR'
        elif obj.is_hod:
            return 'HOD'
        elif obj.is_unit_head:
            return 'Unit Head'
        elif obj.is_manager:
            return 'Manager'
        else:
            return 'Employee'
    
    def to_representation(self, instance):
        """Customize the representation of the user data"""
        data = super().to_representation(instance)
        
        # Add login history
        data['login_history'] = LoginHistorySerializer(
            instance.login_history.all()[:5],  # Get last 5 login attempts
            many=True
        ).data
        
        return data
    


# Add a serializer for login history
class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = [
            'login_time',
            'device_type',
            'browser',
            'os_type',
            'user_ip',
            'login_status',
            'is_secure'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[
            ('employee', 'Employee'),
            ('hod', 'HOD'),
            ('unit_head', 'Unit Head'),
            ('manager', 'Manager'),
            ('hr', 'HR'),
            ('superuser', 'Superuser'),
        ],
        write_only=True
    )
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username',
            'sur_name',
            'first_name',
            'password',
            'password2',
            'role',
        ]

    def validate(self, data):
        """Validate the registration data"""
        request = self.context.get('request')
        
        # Ensure passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        
        # Role-based validation
        role = data.get('role')
        if not (request.user.is_superuser or request.user.is_hr):
            # HOD and Unit Head can only create employees
            if role != 'employee':
                raise serializers.ValidationError({
                    "role": "You can only register employees."
                })
        
        return data

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)
        validated_data.pop('password2', None)

        if role == 'employee':
            user = User.objects.create_employee(**validated_data)
        elif role == 'hod':
            user = User.objects.create_hod(**validated_data)
        elif role == 'unit_head':
            user = User.objects.create_unit_head(**validated_data)
        elif role == 'manager':
            user = User.objects.create_manager(**validated_data)
        elif role == 'hr':
            user = User.objects.create_hr(**validated_data)
        elif role == 'superuser':
            user = User.objects.create_superuser(**validated_data)
        else:
            raise serializers.ValidationError({
                'role': 'Invalid role specified.'
            })

        if password:
            user.set_password(password)
            user.save()

        return user
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the original token data
        data = super().validate(attrs)
        
        # Get request information
        request = self.context.get('request')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR')
        
        # Create login history entry
        LoginHistory.objects.create(
            user=self.user,
            user_agent=user_agent,
            user_ip=ip_address,
            login_status='success',
            device_type='desktop',  # Default to desktop, can be updated based on user agent
            browser=self._get_browser(user_agent),
            browser_version=self._get_browser_version(user_agent),
            os_type=self._get_os_type(user_agent),
            os_version=self._get_os_version(user_agent),
            is_secure=request.is_secure(),
        )
        
        return data
    
    def _get_browser(self, user_agent):
        # Simple browser detection
        if 'Chrome' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent:
            return 'Safari'
        elif 'Edge' in user_agent:
            return 'Edge'
        return 'Unknown'
    
    def _get_browser_version(self, user_agent):
        # This is a simplified version - you might want to use a proper user agent parser
        return 'Unknown'
    
    def _get_os_type(self, user_agent):
        if 'Windows' in user_agent:
            return 'Windows'
        elif 'Mac' in user_agent:
            return 'MacOS'
        elif 'Linux' in user_agent:
            return 'Linux'
        elif 'Android' in user_agent:
            return 'Android'
        elif 'iOS' in user_agent:
            return 'iOS'
        return 'Unknown'
    
    def _get_os_version(self, user_agent):
        # This is a simplified version - you might want to use a proper user agent parser
        return 'Unknown'

# Add this new serializer class
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            'username',
            'password', 
            'user_permissions', 
            'groups', 
            'last_login'
        ]
        
    def validate_email(self, value):
        """Validate email uniqueness"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class UserProfileAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'sur_name',
            'first_name',
            'other_name',
            'phone',
            'email',
            'designation',
            'dept',
            'unit',
            'address',
            'emergency_contact',
            'emergency_phone',
            'blood_group',
            'marital_status',
            'residential_address',
            'permanent_address',
            'state_of_origin',
            'local_government',
            'nationality',
            'religion',
            'avatar',
            'employment_type',
            'job_title',
            'grade_level',
            'is_active'
        ]
        
    def validate_email(self, value):
        """Validate email uniqueness"""
        user_id = self.context.get('user_id')
        if User.objects.exclude(pk=user_id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class UserProfileByIDUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'sur_name',
            'first_name',
            'other_name',
            'phone',
            'email',
            'designation',
            'dept',
            'unit',
            'address',
            'emergency_contact',
            'emergency_phone',
            'blood_group',
            'marital_status',
            'residential_address',
            'permanent_address',
            'state_of_origin',
            'local_government',
            'nationality',
            'religion',
            'avatar',
            'employment_type',
            'job_title',
            'grade_level',
            'is_active'
        ]
        
    def validate_email(self, value):
        """Validate email uniqueness"""
        record_id = self.context.get('record_id')
        if User.objects.exclude(pk=record_id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
class UsernamePasswordUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    password2 = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2']

    def validate(self, data):
        if 'password' in data:
            if data.get('password') != data.get('password2'):
                raise serializers.ValidationError({"password": "Passwords do not match."})
            validate_password(data['password'], self.instance)
        return data

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class UserCredentialsUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)
    new_username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['new_username', 'new_password', 'confirm_password']

    def validate(self, data):
        # If updating password, validate new password
        if data.get('new_password'):
            if data['new_password'] != data.get('confirm_password'):
                raise serializers.ValidationError({"new_password": "New passwords do not match."})
            validate_password(data['new_password'], self.instance)

        # If updating username, check if it's already taken
        if data.get('new_username'):
            if User.objects.exclude(pk=self.instance.pk).filter(username=data['new_username']).exists():
                raise serializers.ValidationError({"new_username": "This username is already taken."})

        return data

    def update(self, instance, validated_data):
        # Update username if provided
        if validated_data.get('new_username'):
            instance.username = validated_data['new_username']

        # Update password if provided
        if validated_data.get('new_password'):
            instance.set_password(validated_data['new_password'])

        instance.save()
        return instance

# Allow superuser to update any password
class AdminPasswordUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['new_password', 'confirm_password']

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        validate_password(data['new_password'], self.instance)
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    dept = DepartmentSerializers(read_only=True)
    unit = UnitSerializers(read_only=True)
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'email',
            'phone',
            'designation',
            'dept',
            'unit',
            'role',
            'is_active',
            'date_joined'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.sur_name}"

    def get_role(self, obj):
        if obj.is_superuser:
            return 'Superuser'
        elif obj.is_hr:
            return 'HR'
        elif obj.is_hod:
            return 'HOD'
        elif obj.is_unit_head:
            return 'Unit Head'
        elif obj.is_manager:
            return 'Manager'
        else:
            return 'Employee'
        
class AccountStatusHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    changed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = AccountStatusHistory
        fields = [
            'id',
            'user',
            'previous_status',
            'new_status',
            'status_change',
            'reason',
            'changed_by',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_change']

class UserMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal serializer for user information in account status history.
    Includes only essential fields needed for status history display.
    """
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'role',
            'is_active'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.sur_name}"
    
    def get_role(self, obj):
        if obj.is_superuser:
            return 'Superuser'
        elif obj.is_hr:
            return 'HR'
        elif obj.is_hod:
            return 'HOD'
        elif obj.is_unit_head:
            return 'Unit Head'
        elif obj.is_manager:
            return 'Manager'
        else:
            return 'Employee'

class AccountStatusHistoryListSerializer(serializers.ModelSerializer):
    """
    A simplified serializer for account status history listing.
    Uses minimal user information to reduce response payload.
    """
    user = UserMinimalSerializer(read_only=True)
    changed_by = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = AccountStatusHistory
        fields = [
            'id',
            'user',
            'previous_status',
            'new_status',
            'status_change',
            'reason',
            'changed_by',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status_change']