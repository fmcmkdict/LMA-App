from django.shortcuts import render, get_object_or_404

from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import *

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied

from .models import UserAccounts
# from core.api.permissions import IsAdminOrHROrHOD, CanRegisterUser,CanUpdateOwnUsernameOrPassword
from core.api.permissions import *
from django.db.models import Q


class UserRegistrationAPIView(GenericAPIView):
    """
    A view to register new users.
    Only accessible by:
    - Superusers (can register any user)
    - HR (can register any user)
    - HOD (can only register users in their department)
    - Unit Head (can only register users in their unit)
    """
    permission_classes = [IsAuthenticated, CanRegisterUser]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request, *arg, **kwargs):
        # Check department/unit permissions
        dept_id = request.data.get('dept')
        unit_id = request.data.get('unit')
        
        if not (request.user.is_superuser or request.user.is_hr):
            # For HOD, check if department matches
            if request.user.is_hod and dept_id:
                if int(dept_id) != request.user.dept.id:
                    raise PermissionDenied("You can only register users in your department.")
            
            # For Unit Head, check if unit matches
            if request.user.is_unit_head and unit_id:
                if int(unit_id) != request.user.unit.id:
                    raise PermissionDenied("You can only register users in your unit.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        
        return Response(data, status=status.HTTP_201_CREATED)
    
class UserProfileView(RetrieveAPIView):
    """
    A view to retrieve the authenticated user's profile details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        """
        Returns the authenticated user's profile.
        """
        return self.request.user

class UserProfileUpdateView(UpdateAPIView):
    """
    A view to update the authenticated user's profile details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # Added JSONParser
    
    def get_object(self):
        """
        Returns the authenticated user's profile.
        """
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """
        Handle the update operation with partial updates support.
        """
        partial = kwargs.pop('partial', True)  # Allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return the updated user data using the main UserSerializer
        return Response(
            UserSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

class UserProfileAdminUpdateView(UpdateAPIView):
    """
    A view to update any user's profile details by user ID.
    Only accessible by:
    - Superusers (can update any user)
    - HR (can update any user)
    - HOD (can only update users in their department)
    - Unit Head (can only update users in their unit)
    """
    permission_classes = [IsAuthenticated, IsAdminOrHROrHOD]
    serializer_class = UserProfileAdminUpdateSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_object(self):
        """
        Returns the user profile to be updated based on user_id
        """
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, id=user_id)
    
    def update(self, request, *args, **kwargs):
        """
        Handle the update operation with partial updates support.
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        
        # Add user_id to serializer context for email validation
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial,
            context={'user_id': instance.id}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return the updated user data using the main UserSerializer
        return Response(
            UserSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

class UserProfileByIDUpdateView(UpdateAPIView):
    """
    A view to update a user's profile details by record ID.
    Only accessible by:
    - Superusers (can update any user)
    - HR (can update any user)
    - HOD (can only update users in their department)
    - Unit Head (can only update users in their unit)
    """
    permission_classes = [IsAuthenticated, IsAdminOrHROrHOD]
    serializer_class = UserProfileByIDUpdateSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_object(self):
        """
        Returns the user profile to be updated based on record_id
        """
        record_id = self.kwargs.get('record_id')
        user = get_object_or_404(User, id=record_id)
         
        return user
    
    def update(self, request, *args, **kwargs):
        """
        Handle the update operation with partial updates support.
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        
        # Add record_id to serializer context for email validation
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial,
            context={'record_id': instance.id}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return the updated user data using the main UserSerializer
        return Response(
            UserSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )

# update own username or password
class UserCredentialsUpdateView(UpdateAPIView):
    """
    A view to update user's own username and password.
    Requires current password verification.
    """
    serializer_class = UserCredentialsUpdateSerializer
    permission_classes = [IsAuthenticated, CanUpdateOwnCredentials]
    http_method_names = ['patch']  # Only allow PATCH method

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return success message
        return Response({
            "message": "Credentials updated successfully",
            "user": UserSerializer(instance, context=self.get_serializer_context()).data
        }, status=status.HTTP_200_OK)

class AdminPasswordUpdateView(UpdateAPIView):
    """
    A view for superusers to update any user's password.
    Only accessible by superusers.
    """
    serializer_class = AdminPasswordUpdateSerializer
    permission_classes = [IsAuthenticated, CanUpdateUserPassword]
    http_method_names = ['patch']  # Only allow PATCH method

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, id=user_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return success message
        return Response({
            "message": f"Password updated successfully for user {instance.username}",
            "user": UserSerializer(instance, context=self.get_serializer_context()).data
        }, status=status.HTTP_200_OK)

class UserListView(ListAPIView):
    """
    A view to list users based on the user's role:
    - Superusers can see all users
    - HR can see all users
    - HOD can only see users in their department
    - Unit Head can only see users in their unit
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, CanListUsers]
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset with select_related for dept and unit
        queryset = User.objects.select_related('dept', 'unit').all()
        
        # Apply filters based on user role
        if user.is_superuser or user.is_hr:
            # Superusers and HR can see all users
            return queryset
        
        elif user.is_hod:
            # HOD can only see users in their department
            return queryset.filter(dept=user.dept)
        
        elif user.is_unit_head:
            # Unit Head can only see users in their unit
            return queryset.filter(unit=user.unit)
        
        return User.objects.none()  # Return empty queryset for unauthorized users

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Apply search filter if provided
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(sur_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Apply department filter if provided
        dept_id = request.query_params.get('dept', None)
        if dept_id:
            queryset = queryset.filter(dept_id=dept_id)
        
        # Apply unit filter if provided
        unit_id = request.query_params.get('unit', None)
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        # Apply role filter if provided
        role = request.query_params.get('role', None)
        if role:
            if role == 'superuser':
                queryset = queryset.filter(is_superuser=True)
            elif role == 'hr':
                queryset = queryset.filter(is_hr=True)
            elif role == 'hod':
                queryset = queryset.filter(is_hod=True)
            elif role == 'unit_head':
                queryset = queryset.filter(is_unit_head=True)
            elif role == 'manager':
                queryset = queryset.filter(is_manager=True)
            elif role == 'employee':
                queryset = queryset.filter(
                    is_superuser=False,
                    is_hr=False,
                    is_hod=False,
                    is_unit_head=False,
                    is_manager=False
                )
        
        # Apply active status filter if provided
        is_active = request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Add pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
# Endpoint to manage account status
class AccountStatusHistoryView(ListAPIView):
    """
    View to list account status history with statistics.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head).
    """
    serializer_class = AccountStatusHistoryListSerializer  # Use the new serializer
    permission_classes = [IsAuthenticated, CanManageAccountStatus]
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset with optimized select_related
        queryset = AccountStatusHistory.objects.select_related(
            'user',
            'changed_by'
        ).only(
            'id',
            'previous_status',
            'new_status',
            'status_change',
            'reason',
            'created_at',
            'user__id',
            'user__username',
            'user__first_name',
            'user__sur_name',
            'user__is_active',
            'user__is_superuser',
            'user__is_hr',
            'user__is_hod',
            'user__is_unit_head',
            'user__is_manager',
            'changed_by__id',
            'changed_by__username',
            'changed_by__first_name',
            'changed_by__sur_name',
            'changed_by__is_active',
            'changed_by__is_superuser',
            'changed_by__is_hr',
            'changed_by__is_hod',
            'changed_by__is_unit_head',
            'changed_by__is_manager'
        ).all()
        
        # Apply filters based on user role
        if user.is_superuser or user.is_hr:
            return queryset
        elif user.is_hod:
            return queryset.filter(user__dept=user.dept)
        elif user.is_unit_head:
            return queryset.filter(user__unit=user.unit)
        
        return AccountStatusHistory.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate statistics
        total_count = queryset.count()
        activated_count = queryset.filter(status_change='ACTIVATED').count()
        deactivated_count = queryset.filter(status_change='DEACTIVATED').count()
        
        # Apply date range filter if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__range=[start_date, end_date]
            )
        
        # Apply user filter if provided
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Apply status change filter if provided
        status_change = request.query_params.get('status_change')
        if status_change:
            queryset = queryset.filter(status_change=status_change)
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add statistics to the response
            response.data['statistics'] = {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
        })


class AccountStatusChangeView(UpdateAPIView):
    """
    View to change a user's account status.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head).
    """
    serializer_class = UserProfileAdminUpdateSerializer
    permission_classes = [IsAuthenticated, CanManageAccountStatus]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, id=user_id)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_status = instance.is_active
        
        # Update the user's status
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Create status history entry
        AccountStatusHistory.objects.create(
            user=instance,
            previous_status=previous_status,
            new_status=instance.is_active,
            reason=request.data.get('reason', ''),
            changed_by=request.user
        )
        
        return Response(
            UserSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK
        )
        
# user specific account status detail given a user ID 
class UserAccountStatusHistoryView(ListAPIView):
    """
    View to get account status history for a specific user.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head).
    """
    serializer_class = AccountStatusHistoryListSerializer
    permission_classes = [IsAuthenticated, CanManageAccountStatus]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
       
        
        return AccountStatusHistory.objects.filter(user=user).select_related(
            'user',
            'changed_by'
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate statistics for this user
        total_count = queryset.count()
        activated_count = queryset.filter(status_change='ACTIVATED').count()
        deactivated_count = queryset.filter(status_change='DEACTIVATED').count()
        
        # Apply date range filter if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__range=[start_date, end_date]
            )
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add statistics to the response
            response.data['statistics'] = {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
        }) 

# View to allow  user to view his or her account
class OwnAccountStatusHistoryView(ListAPIView):
    """
    View for users to see their own account status history.
    Only accessible by the authenticated user for their own account.
    """
    serializer_class = AccountStatusHistoryListSerializer
    permission_classes = [IsAuthenticated, CanViewOwnAccountStatus]
    
    def get_queryset(self):
        """
        Returns the account status history for the authenticated user.
        """
        return AccountStatusHistory.objects.filter(
            user=self.request.user
        ).select_related(
            'user',
            'changed_by'
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate statistics for the user
        total_count = queryset.count()
        activated_count = queryset.filter(status_change='ACTIVATED').count()
        deactivated_count = queryset.filter(status_change='DEACTIVATED').count()
        
        # Apply date range filter if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__range=[start_date, end_date]
            )
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add statistics to the response
            response.data['statistics'] = {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': {
                'total_count': total_count,
                'activated_count': activated_count,
                'deactivated_count': deactivated_count,
                'activation_rate': round((activated_count / total_count * 100) if total_count > 0 else 0, 2),
                'deactivation_rate': round((deactivated_count / total_count * 100) if total_count > 0 else 0, 2)
            }
        })

class AccountStatusDetailView(RetrieveAPIView):
    """
    View to get detailed account status information for a specific record.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head) or the user themselves.
    """
    serializer_class = AccountStatusHistorySerializer
    permission_classes = [IsAuthenticated, CanViewAccountStatusDetail]
    
    def get_object(self):
        record_id = self.kwargs.get('record_id')
        return get_object_or_404(AccountStatusHistory, id=record_id)

class LoginHistoryListView(ListAPIView):
    """
    View to list all login history with summary statistics.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head) or users for their own history.
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated, CanViewLoginHistory]
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset with select_related for user
        queryset = LoginHistory.objects.select_related('user').all()
        
        # Apply filters based on user role
        if user.is_superuser or user.is_hr:
            return queryset
        elif user.is_hod:
            return queryset.filter(user__dept=user.dept)
        elif user.is_unit_head:
            return queryset.filter(user__unit=user.unit)
        else:
            return queryset.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate statistics
        total_logins = queryset.count()
        successful_logins = queryset.filter(login_status='success').count()
        failed_logins = queryset.filter(login_status='failed').count()
        blocked_logins = queryset.filter(login_status='blocked').count()
        
        # Device statistics
        desktop_logins = queryset.filter(device_type='desktop').count()
        mobile_logins = queryset.filter(device_type='mobile').count()
        tablet_logins = queryset.filter(device_type='tablet').count()
        
        # Browser statistics
        browser_stats = queryset.values('browser').annotate(count=models.Count('browser'))
        
        # OS statistics
        os_stats = queryset.values('os_type').annotate(count=models.Count('os_type'))
        
        # Apply date range filter if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                login_time__range=[start_date, end_date]
            )
        
        # Apply user filter if provided
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Apply status filter if provided
        login_status = request.query_params.get('login_status')
        if login_status:
            queryset = queryset.filter(login_status=login_status)
        
        # Apply device type filter if provided
        device_type = request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add statistics to the response
            response.data['statistics'] = {
                'total_logins': total_logins,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'blocked_logins': blocked_logins,
                'success_rate': round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'failure_rate': round((failed_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'block_rate': round((blocked_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'device_breakdown': {
                    'desktop': desktop_logins,
                    'mobile': mobile_logins,
                    'tablet': tablet_logins
                },
                'browser_breakdown': list(browser_stats),
                'os_breakdown': list(os_stats)
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': {
                'total_logins': total_logins,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'blocked_logins': blocked_logins,
                'success_rate': round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'failure_rate': round((failed_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'block_rate': round((blocked_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'device_breakdown': {
                    'desktop': desktop_logins,
                    'mobile': mobile_logins,
                    'tablet': tablet_logins
                },
                'browser_breakdown': list(browser_stats),
                'os_breakdown': list(os_stats)
            }
        })
        
# view to list user login history using user_id
class UserLoginHistoryView(ListAPIView):
    """
    View to get login history for a specific user with summary statistics.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head) or the user themselves.
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated, CanViewLoginHistory]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        request_user = self.request.user
        
        # Check if the requesting user has permission to view this user's history
        if not (request_user.is_superuser or request_user.is_hr or 
                (request_user.is_hod and user.dept == request_user.dept) or
                (request_user.is_unit_head and user.unit == request_user.unit) or
                request_user.id == user_id):
            raise PermissionDenied("You don't have permission to view this user's login history.")
        
        return LoginHistory.objects.filter(user=user).select_related('user')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate statistics
        total_logins = queryset.count()
        successful_logins = queryset.filter(login_status='success').count()
        failed_logins = queryset.filter(login_status='failed').count()
        blocked_logins = queryset.filter(login_status='blocked').count()
        
        # Device statistics
        desktop_logins = queryset.filter(device_type='desktop').count()
        mobile_logins = queryset.filter(device_type='mobile').count()
        tablet_logins = queryset.filter(device_type='tablet').count()
        
        # Browser statistics
        browser_stats = queryset.values('browser').annotate(count=models.Count('browser'))
        
        # OS statistics
        os_stats = queryset.values('os_type').annotate(count=models.Count('os_type'))
        
        # Apply date range filter if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                login_time__range=[start_date, end_date]
            )
        
        # Apply status filter if provided
        login_status = request.query_params.get('login_status')
        if login_status:
            queryset = queryset.filter(login_status=login_status)
        
        # Apply device type filter if provided
        device_type = request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add statistics to the response
            response.data['statistics'] = {
                'total_logins': total_logins,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'blocked_logins': blocked_logins,
                'success_rate': round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'failure_rate': round((failed_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'block_rate': round((blocked_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'device_breakdown': {
                    'desktop': desktop_logins,
                    'mobile': mobile_logins,
                    'tablet': tablet_logins
                },
                'browser_breakdown': list(browser_stats),
                'os_breakdown': list(os_stats),
                'last_login': queryset.order_by('-login_time').first().login_time if queryset.exists() else None,
                'last_failed_login': queryset.filter(login_status='failed').order_by('-login_time').first().login_time if queryset.filter(login_status='failed').exists() else None
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': {
                'total_logins': total_logins,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'blocked_logins': blocked_logins,
                'success_rate': round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'failure_rate': round((failed_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'block_rate': round((blocked_logins / total_logins * 100) if total_logins > 0 else 0, 2),
                'device_breakdown': {
                    'desktop': desktop_logins,
                    'mobile': mobile_logins,
                    'tablet': tablet_logins
                },
                'browser_breakdown': list(browser_stats),
                'os_breakdown': list(os_stats),
                'last_login': queryset.order_by('-login_time').first().login_time if queryset.exists() else None,
                'last_failed_login': queryset.filter(login_status='failed').order_by('-login_time').first().login_time if queryset.filter(login_status='failed').exists() else None
            }
        })

class LoginHistoryDetailView(RetrieveAPIView):
    """
    View to get detailed information about a specific login history record.
    Only accessible by authorized users (superuser, HR, HOD, Unit Head) or the user themselves.
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated, CanViewLoginHistory]
    
    def get_object(self):
        record_id = self.kwargs.get('record_id')
        login_record = get_object_or_404(LoginHistory, id=record_id)
        
        # Check if the requesting user has permission to view this record
        return login_record