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
        ('cancelled', 'Cancelled')
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="leave_types")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.TextField()
    leave_last_taken =models.DateField()
    number_of_days = models.IntegerField()
    deductible_leave = models.PositiveIntegerField(null=True, blank=True)
    leave_code = models.CharField(max_length=250,unique=True)
    ip_address = models.GenericIPAddressField(null=True,blank=True)
    user_agent = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # include address and where leave is to be spent
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_leaves", null=True, blank=True)
    recommended_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="leave_recommendations", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.employee.sur_name
    
    def get_location(self):
        if self.ip_address:
            geo = GeoIP2()
            try:
                location = geo.city(self.ip_address)
                return f"{location['city']}, {location['country_name']}"
            except Exception:
                return "Unknown Location"
        return "Unknown Location"
    

# This stores holidays available in a year
class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(unique=True)
    year = models.PositiveIntegerField()
    description = models.CharField(max_length=200)

    class Meta:
        ordering = ["date"]
        unique_together = ("date", "year")
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"

    def __str__(self):
        return f"{self.name} ({self.date})"
    
    # 
    def compute_leave_days(start_date, end_date):
        
        """Compute actual leave days excluding weekends and public holidays."""
        current_date = start_date
        leave_days = 0

        while current_date <= end_date:
            # Skip weekends (Saturday & Sunday)
            if current_date.weekday() in [5, 6]:  
                current_date += timedelta(days=1)
                continue

            # Skip public holidays
            if Holiday.objects.filter(date=current_date).exists():
                current_date += timedelta(days=1)
                continue

            leave_days += 1
            current_date += timedelta(days=1)

        return leave_days
    

    
     


    
    
