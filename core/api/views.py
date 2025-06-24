from django.shortcuts import render
from datetime import datetime

# generics view classes
# from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import generics

# APIView classes
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from .serializers import *

from core.models import *
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


# import validation errors
from rest_framework.exceptions import ValidationError
from core.utils.utilities import *
from core.api.permissions import *


# using concrete views
class DeptCreateList(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializers
    permission_classes = [IsAuthenticated]

# For GET (one), PUT/PATCH (update), DELETE
class DeptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializers

# class DeptListCreateAV(APIView):
#     # authentication_classes = [IsAuthenticated]
#     # permission_classes = [IsAdminUser]
    
#     # Handle GET (list all) and POST (create)
#     def get(self, request):
#         depts = Department.objects.all()
#         serializer = DepartmentSerializers(depts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     def post(self, request):
#         serializer = DepartmentSerializers(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Department Details
# class DeptDetailAV(APIView):
#     # Uncomment if needed
#     # permission_classes = [IsAdminOrReadOnly]
#     # throttle_classes = [AnonRateThrottle]

#     def get_object(self, pk):
#         return get_object_or_404(Department, pk=pk)

#     def get(self, request, pk):
#         dept = self.get_object(pk)
#         serializer = DepartmentSerializers(dept)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         product = self.get_object(pk)
#         serializer = DepartmentSerializers(product, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         dept = self.get_object(pk)
#         dept.delete()
#         return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
   


class UnitCreateList(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializers
    

class UnitsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all()
    serializer_class= UnitSerializers
    
class LeaveTypeCreateList(generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class= LeaveTypeSerializers
    permission_classes = [IsAuthenticated]
    
class LeaveTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializers
    

class HolidayCreateList(generics.ListCreateAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializers
    
class HolidayDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializers
    
    
class CreateLeaveApplication(generics.CreateAPIView):
    serializer_class = LeaveRequestSerializers
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LeaveRequest.objects.all()
    
    def perform_create(self, serializer):
        user = self.request.user
        leave_type = serializer.validated_data['leave_type']
        start_date = serializer.validated_data['start_date']
        leave_days = serializer.validated_data['number_of_days']
        deductible_leave = serializer.validated_data.get('deductible_leave', 0)
        current_year = datetime.now().year
        end_date = calc_end_date(start_date, leave_days)

        # Check if the user has any existing approved or pending leave requests
        existing_request = LeaveRequest.objects.filter(
            employee=user,
            status__in=['pending', 'approved']
        ).exists()

        if existing_request:
            raise PermissionDenied(detail="You already have a pending or approved leave request.")

        # Check if the user has already applied for the same leave type in the current year
        same_type_request_this_year = LeaveRequest.objects.filter(
            employee=user,
            leave_type=leave_type,
            start_date__year=current_year
        ).exists()

        if same_type_request_this_year:
            raise PermissionDenied(detail="You have already applied for this type of leave this year.")

        # Get or create leave balance for the current year
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=user,
            leave_type=leave_type,
            year=current_year,
            defaults={
                'total_days': 30,  # You might want to make this configurable
                'days_used': 0,
                'days_remaining': 30
            }
        )

        # Calculate actual leave days after deduction
        actual_leave_days = max(0, leave_days - deductible_leave)

        # Check if user has enough leave days remaining
        if actual_leave_days > leave_balance.days_remaining:
            raise PermissionDenied(
                detail=f"Insufficient leave balance. You have {leave_balance.days_remaining} days remaining."
            )

        # Update leave balance
        leave_balance.days_used += actual_leave_days
        leave_balance.save()

        # Save the leave request with actual leave days
        serializer.save(
            employee=user,
            end_date=end_date,
            number_of_days=actual_leave_days,
            deductible_leave=deductible_leave
        )
        
# list all leave request
class ListLeaveRequest(generics.ListAPIView):
  
    serializer_class = LeaveRequestSerializers
    
    def get_queryset(self):
        leaveQueryset = LeaveRequest.objects.select_related(
            'employee',
            'leave_type',
            'dept',
            'unit',
            'approved_by',
            'recommended_by'
        ).all()
        
        return leaveQueryset
    
    
# leave request detail
class LeaveRequestDetail(generics.RetrieveAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializers
    

class LeaveRequestUpdate(generics.RetrieveUpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializers
    permission_classes = [IsAuthenticated, IsOwnerOrSuperAdmin]

    def perform_update(self, serializer):
        pk = self.kwargs.get('pk')
        # get the instance being jupdated
        obj = serializer.instance
        # check if leave if still pending
        start_date = serializer.validated_data['start_date']
        leave_days = serializer.validated_data['number_of_days']
        end_date = calc_end_date(start_date, leave_days)
        
        if obj.status !='pending':
            raise ValidationError({"detail":"Update denied! This leave is not in pending state"})
        
        
        # Automatically set the 'recommended_by' field to the current user
        serializer.save(end_date=end_date)
        # serializer.save()
        # serializer.save(recommended_by=self.request.user)
        
        
# recommend leave request
class RecommendLeaveRequest(generics.RetrieveUpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializers
    permission_classes = [IsAuthenticated, IsUnitHeadRecommend]

    def perform_update(self, serializer):
        pk = self.kwargs.get('pk')
        # get the instance being updated
        obj = serializer.instance
        
        
        # check if leave if still
        if obj.recommended_by is not None:
            raise ValidationError({"detail": "Leave already recommended"})

        if obj.status != 'pending':
            raise ValidationError({"detail": "Update denied! This leave is not in pending state"})

        serializer.save(recommended_by=self.request.user)
        
# approve leave
class ApproveRejectLeaveRequest(generics.RetrieveUpdateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializers
    permission_classes = [IsAuthenticated, IsHodOrManager]

    def perform_update(self, serializer):
        pk = self.kwargs.get('pk')
        # get the instance being updated
        obj = serializer.instance
        
        
        # check if leave is still opne
        if obj.recommended_by is None:
            raise ValidationError({"detail": "Leave is not recommended!"})

        if obj.status == 'approved' or obj.status == 'rejected' or obj.status == 'cancelled' or obj.status == 'exhausted':
            raise ValidationError({"detail": "Denied! Action has been taken on this leave already"})

        serializer.save(approved_by=self.request.user)
  

# Search for leave application using surname, staff Number
class LeaveRequestSearch(generics.ListAPIView):
    
    serializer_class  = LeaveRequestSerializers
    
    def get_queryset(self):
       
        queryset = LeaveRequest.objects.select_related( 'employee',
            'leave_type',
            'dept',
            'unit',
            'approved_by',
            'recommended_by'
            )
        
        # search_term = self.request.query_params.get('search', None)
        search_term = self.kwargs.get('search')
        print(search_term)

        if search_term:
            queryset = queryset.filter(
                Q(employee__sur_name__icontains=search_term)
                # |# Q(staff__staff_number__icontains=search_term)
            )
        return queryset
        

class  DeleteLeaveRequest(generics.RetrieveDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializers
    permission_classes= [IsAuthenticated]
    
    

# list all leaves by Department given a dept ID
class ListDeptLeaveRequest(generics.ListAPIView):
  
    serializer_class = LeaveRequestSerializers
    
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        leaveQueryset = LeaveRequest.objects.select_related(
            'employee',
            'leave_type',
            'dept',
            'unit',
            'approved_by',
            'recommended_by'
        ).filter(dept=pk)
        
        return leaveQueryset
    
# Leave requests by unit given a unit ID
class ListUnitLeaveRequest(generics.ListAPIView):
  
    serializer_class = LeaveRequestSerializers
    
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        leaveQueryset = LeaveRequest.objects.select_related(
            'employee',
            'leave_type',
            'dept',
            'unit',
            'approved_by',
            'recommended_by'
        ).filter(unit=pk)
        
        return leaveQueryset
    
# list all leave request given a user ID
class ListUserLeaveRequest(generics.ListAPIView):
  
    serializer_class = LeaveRequestSerializers
    
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        leaveQueryset = LeaveRequest.objects.select_related(
            'employee',
            'leave_type',
            'dept',
            'unit',
            'approved_by',
            'recommended_by'
        ).filter(employee=pk)
        
        return leaveQueryset