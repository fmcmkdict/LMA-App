from UserAccounts.models import *

from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# import authenticate for Login serializer
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields="__all__"
        
        
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
        fields = ['username','sur_name','first_name','password','password2', 'role','dept','unit']
        # fields = '__all__'

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
            raise serializers.ValidationError({'role': 'Invalid role specified.'})

        if password:
            user.set_password(password)
            user.save()

        return user
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    
    def validate(self, attrs):
        # return super().validate(attrs)
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        
        raise serializers.ValidationError({"error":"Incorrect Credentials"})

        
class NotInUseRegistrationSerializer(serializers.ModelSerializer):
    
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ("id","username","sur_name","first_name","password1","password2")
        extra_kwargs = {"password": {"write_only": True}}
        
        
    def validate(self, data):
        # Ensure the two passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
    
        # Check for short password
        if len(data['password1']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
    
        return data

    def create(self, validated_data):
        # Remove password1 and password2 from the validated data
        # TODO pop upvalues for roles and decide how to which made to call to create the user
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        # Create a new user
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    
    
    
    
    
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['id'] = user.id
#         token['username'] = user.username
#         token['sur_name'] = user.sur_name
#         token['first_name'] = user.first_name
   

#         return token