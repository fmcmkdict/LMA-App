from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    
    def create_user(self, username, password, **extra_fields):
        
        if not username:
            raise ValueError('User must have a username and must be unique')
    
        user = self.model(username=username,**extra_fields)
        user.set_password(password)
        
        # when using multple databases
        # user.save(using=self._db)
        user.save()
        return user
    

    # method to create other roles
    def create_employee(self, username=None, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        user = self.create_user(username,password,**extra_fields)
        user.save()
        
        return user
    
    def create_hod(self, username=None, password=None, **extra_fields):
        
        """Creates and returns a HOD user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_hod', True)
    
        user = self.create_user(username, password, **extra_fields)
        user.save()
        return user

    def create_unit_head(self, username=None, password=None, **extra_fields):
        """Creates and returns a Unit Head user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_unit_head', True)
        
        user = self.create_user(username, password, **extra_fields)
        user.save()
        return user

    def create_manager(self, username=None, password=None, **extra_fields):
        """Creates and returns a Manager user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_manager', True)
        
        user = self.create_user(username, password, **extra_fields)
        user.save()
        return user
    
    
    def create_hr(self,username=None,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_hr', True)
        user = self.create_user(username,password, **extra_fields)
        
        user.save()
        return user
    
    
    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_manager', True)
        extra_fields.setdefault('is_hr', True)
        extra_fields.setdefault('is_unit_head', True)
        extra_fields.setdefault('is_hod', True)
        user = self.create_user(username,password, **extra_fields)
       
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
    gender = models.CharField(max_length=50,blank=True,null=True)
    designation = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=50,blank=True,null=True)
    dept = models.ForeignKey('core.Department',on_delete=models.CASCADE, related_name='userdept',blank=True,null=True)
    unit = models.ForeignKey('core.Unit', on_delete=models.CASCADE,related_name='userunits',blank=True,null=True)
    dob = models.DateField(blank=True,null=True)
    avatar = models.ImageField(null=True,blank=True)
    email = models.EmailField(max_length=255,blank=True,null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # New fields
    id_card_mumber = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Unique employee identification number")
    address = models.TextField(blank=True, null=True, help_text="Current residential address")
    emergency_contact = models.CharField(max_length=255, blank=True, null=True, help_text="Emergency contact person")
    emergency_phone = models.CharField(max_length=50, blank=True, null=True, help_text="Emergency contact phone number")
    blood_group = models.CharField(max_length=10, blank=True, null=True, help_text="Blood group of the employee")
    marital_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed')
    ])
    
    # Identification
    ippis_number = models.CharField(max_length=50, null=True, blank=True, help_text="Integrated Personnel and Payroll Information System number")
    open_number = models.CharField(max_length=50, null=True, blank=True, help_text="Open number for employee identification")
    secret_number = models.CharField(max_length=50, null=True, blank=True, help_text="Secret number for employee identification")
    
    # Employment Information
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('contract', 'Contract'),
            ('intern', 'Intern')
        ],
        default='full_time'
    )
    job_title = models.CharField(max_length=100, null=True, blank=True)
    grade_level = models.CharField(max_length=20, null=True, blank=True)
    
    # Address Information
    residential_address = models.TextField(null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    state_of_origin = models.CharField(max_length=50, null=True, blank=True)
    local_government = models.CharField(max_length=50, null=True, blank=True)
    
    # Personal Information
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single'),
            ('married', 'Married'),
            ('divorced', 'Divorced'),
            ('widowed', 'Widowed')
        ],
        null=True, blank=True
    )
    nationality = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)
    is_unit_head = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    
    
    REQUIRED_FIELDS = ['first_name', 'sur_name']
    
    # REQUIRED_FIELDS=[]

    def __str__(self):
        return self.sur_name

    def get_full_name(self):
        return f"{self.first_name} {self.sur_name}"

    def get_short_name(self):
        return self.first_name


class AccountStatusHistory(models.Model):
    """
    Tracks the history of account activation and deactivation status changes.
    """
    STATUS_CHOICES = (
        ('ACTIVATED', 'Activated'),
        ('DEACTIVATED', 'Deactivated'),
    )

    user = models.ForeignKey(UserAccounts, on_delete=models.CASCADE, related_name='account_status_history')
    previous_status = models.BooleanField(help_text="Previous active status of the account")
    new_status = models.BooleanField(help_text="New active status of the account")
    status_change = models.CharField(max_length=20,choices=STATUS_CHOICES,help_text="Type of status change",
        editable=False  # Make it non-editable since it's auto-calculated
    )
    reason = models.TextField(help_text="Reason for the status change",blank=True,null=True)
    changed_by = models.ForeignKey(
        UserAccounts,
        on_delete=models.SET_NULL,
        null=True,
        related_name='account_status_changes',
        help_text="User who made the status change"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Account Status History'
        verbose_name_plural = 'Account Status Histories'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status_change']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.status_change} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate the model data before saving."""
       
        
        # Ensure previous_status and new_status are different
        if self.previous_status == self.new_status:
            raise ValidationError("Previous and new status cannot be the same")
        
        # Validate status_change matches the status transition
        if self.previous_status and not self.new_status:
            if self.status_change != 'DEACTIVATED':
                raise ValidationError("Status change must be 'DEACTIVATED' when deactivating an account")
        elif not self.previous_status and self.new_status:
            if self.status_change != 'ACTIVATED':
                raise ValidationError("Status change must be 'ACTIVATED' when activating an account")

    def save(self, *args, **kwargs):
        # Automatically set status_change based on previous and new status
        if self.previous_status and not self.new_status:
            self.status_change = 'DEACTIVATED'
        elif not self.previous_status and self.new_status:
            self.status_change = 'ACTIVATED'
        
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)



class LoginHistory(models.Model):
    """
    Tracks user login history with detailed information about each login attempt.
    """
    user = models.ForeignKey(
        UserAccounts, 
        on_delete=models.CASCADE, 
        related_name='login_history'
    )
    
    # Device Information
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('other', 'Other')
        ],
        default='desktop'
    )
    device_name = models.CharField(max_length=100, null=True, blank=True)
    os_type = models.CharField(max_length=50, null=True, blank=True)
    os_version = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    browser_version = models.CharField(max_length=50, null=True, blank=True)
    
    # Location Information
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    # Login Details
    user_agent = models.TextField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    login_date = models.DateField(auto_now_add=True)
    login_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('blocked', 'Blocked')
        ],
        default='success'
    )
    failure_reason = models.CharField(max_length=255, null=True, blank=True)
    
    # Additional Information
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=True)
    is_bot = models.BooleanField(default=False)
    is_secure = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        indexes = [
            models.Index(fields=['user', 'login_time']),
            models.Index(fields=['login_status']),
            models.Index(fields=['device_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%Y-%m-%d %H:%M')} - {self.login_status}"

    def save(self, *args, **kwargs):
        # Automatically set device type flags
        if self.device_type == 'mobile':
            self.is_mobile = True
            self.is_tablet = False
            self.is_desktop = False
        elif self.device_type == 'tablet':
            self.is_mobile = False
            self.is_tablet = True
            self.is_desktop = False
        else:
            self.is_mobile = False
            self.is_tablet = False
            self.is_desktop = True
            
        super().save(*args, **kwargs)