from UserAccounts.models import *
from core.models import *

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UnitSerializers(serializers.ModelSerializer):
    
    # This overides the default field representation and create a new field name
    department_name = serializers.CharField(source='dept.name', read_only=True)
    # department_id = serializers.IntegerField(source='dept.id', read_only=True)
    class Meta:
        model = Unit
        fields ='__all__'
        
        
class DepartmentSerializers(serializers.ModelSerializer):
    
    deptunits = UnitSerializers(many=True,read_only=True)
    
    class Meta:
        model= Department
        fields='__all__'
        
class LeaveTypeSerializers(serializers.ModelSerializer):
    
    class Meta:
        model= LeaveType
        fields = '__all__'
        

class LeaveRequestSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        
