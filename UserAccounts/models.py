from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    
    def create_user(self, username, password, **extra_fields):
        
        if not username:
            raise ValueError('User must have a username and must be unique')
    
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        
        # when using multple databases
        # user.save(using=self._db)
        user.save()
        return user
    

    # method to create other roles
    def create_employee(self, username=None, password=None,**extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        user = self.create_user(username,password,**extra_fields)
        user.save()
        
        return user
    
    def create_hod(self, username=None, password=None, **extra_fields):
        
        """Creates and returns a HOD user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_hod', True)
    
        return self.create_user(username, password, **extra_fields)

    def create_unit_head(self, username=None, password=None, **extra_fields):
        """Creates and returns a Unit Head user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_unit_head', True)
        
        return self.create_user(username, password, **extra_fields)

    def create_manager(self, username=None, password=None, **extra_fields):
        """Creates and returns a Manager user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_manager', True)
        return self.create_user(username, password, **extra_fields)
    
    
    def create_hr(self,username=None,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_hr', True)
        user = self.create_user(username,password, **extra_fields)
        user.save()
        
        return user
    
    
    def create_superuser(self, username=None, password=None, **extra_fields):
        user = self.create_user(username,password, **extra_fields)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_manager', True)
        extra_fields.setdefault('is_hr', True)
        extra_fields.setdefault('is_unit_head', True)
        extra_fields.setdefault('is_hod', True)
        user.save()
        return user
    
    
# Create your models here.
class UserAccounts(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=255,unique=True)
    sur_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    other_name = models.CharField(max_length=255,blank=True,null=True)
    date_first_appt = models.DateField(blank=True,null=True)
    date_confirmed = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=50)
    designation = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=50,blank=True,null=True)
    # dept = models.CharField(max_length=255)
    # unit = models.CharField(max_length=255)
    dob = models.DateField(blank=True,null=True)
    avatar = models.ImageField(null=True,blank=True)
    email = models.EmailField(unique=True, max_length=255,blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    # date_joined = models.DateTimeField(default=timezone.now)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)
    is_unit_head = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD ='email'
    
    REQUIRED_FIELDS = ['first_name', 'sur_name']
    
    # REQUIRED_FIELDS=[]

    def __str__(self):
        return self.sur_name

    def get_full_name(self):
        return f"{self.first_name} {self.sur_name}"

    def get_short_name(self):
        return self.first_name




