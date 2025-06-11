from django.db import models
from datetime import timedelta
from django.utils.timezone import now

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2

# This model definition stores information about all depts in the Hosp
# 
class Department(models.Model):
    
    DEPT_TYPES = (
        ('CLINICAL','CLINICAL'),
        ('NON-CLINICAL','NON-CLINICAL')
    )
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=200, choices=DEPT_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        return self.name

        
# This model stores information about units related to a dept

class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='deptunits')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
         return self.name
     
# This model records various types of leave e.g. Annual Leave
class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    number_of_days = models.IntegerField(default=0)
    multiple_times = models.BooleanField(default=False) 
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

    

# This model  stores data for leave request
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('exhausted', 'Exhausted')
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="leave_types")
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="leave_depts")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="leave_units")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    reason = models.TextField()
    leave_last_taken =models.DateField()
    number_of_days = models.IntegerField()
    leave_code = models.CharField(max_length=250,unique=True)
    
    home_address = models.TextField()
    place_to_spend_leave = models.TextField()
    alt_phone = models.CharField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_leaves")
    recommended_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="leave_recommendations", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        return f"{self.employee.sur_name} - {self.start_date} to {self.end_date}"
    
    @property
    def working_days(self):
        """Returns the number of leave days excluding weekends and public holidays."""
        start = self.start_date.date()
        end = self.end_date.date()

        total_days = (end - start).days + 1  # include both start and end date
        leave_days = 0

        for i in range(total_days):
            day = start + timedelta(days=i)
            if day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                continue  # skip weekends
            if Holiday.objects.filter(date=day).exists():
                continue  # skip public holidays
            leave_days += 1

        return leave_days


# This stores holidays available in a year
class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(unique=True)  # Ensures no duplicate dates
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.date}"
    

# This model stores the leave balance for each employee
class LeaveBalance(models.Model):
 
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="leave_type_balances")
    year = models.IntegerField()
    total_days = models.PositiveIntegerField()
    days_used = models.PositiveIntegerField(default=0)
    days_remaining = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type.name} ({self.year})"
    
    def save(self, *args, **kwargs):
        self.days_remaining = self.total_days - self.days_used
        super().save(*args, **kwargs)

    
    
