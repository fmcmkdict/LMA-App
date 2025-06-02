from core.models import *
from datetime import timedelta
from django.utils import timezone

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
    
    
def calculate_end_date(start_date, leave_days):
    day = start_date
    days_added = 0

    while days_added < leave_days:
        day += timedelta(days=1)
        # Skip weekends (Saturday = 5, Sunday = 6)
        if day.weekday() >= 5:
            continue
        # You can also add logic here to skip public holidays
        # Example: if day in PUBLIC_HOLIDAYS:
        #    continue
        
        if Holiday.objects.filter(date=current_date).exists():
                current_date += timedelta(days=1)
                continue

        days_added += 1
        current_date += timedelta(days=1)
            

    return day

# use
def calc_end_date(start_date, leave_days):
    end_date = start_date
    days_added = 0

    while days_added < leave_days:
        end_date += timedelta(days=1)
        
        # Skip weekends (Saturday = 5, Sunday = 6)
        if end_date.weekday() >= 5:
            continue
        
        # Skip public holidays
        if Holiday.objects.filter(date=end_date).exists():
                # current_date += timedelta(days=1)
                continue

        days_added += 1

    return end_date

# 

def compute_end_date(start_date, leave_days):
    """
    Calculate the end date excluding weekends.
    """
    current_date = start_date
    days_counted = 0

    while days_counted < leave_days:
        if current_date.weekday() < 5:  # 0 = Monday, 6 = Sunday
            days_counted += 1
        current_date += timedelta(days=1)

    return current_date - timedelta(days=1)