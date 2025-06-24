from rest_framework import permissions
# from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsOwnerOrAdminHRManager(permissions.BasePermission):
    """
    Custom permission to only allow:
        - the owner of the leave request to edit/cancel their own request
        - Admin, HR, Manager, or Superuser to edit/cancel any request
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is trying to edit/cancel their own leave
        if obj.employee == request.user:
            return True

        # TODO
        # Do we need to allow all admin users to edit leave
        # Check if the user has elevated permissions (admin/hr/manager/superuser)
        # return request.user.is_superuser or request.user.is_hod or request.user.is_hr or request.user.is_manager or request.user.is_unit_head
        if request.user.is_superuser:
            return True
        
        return False
    
class IsOwnerOrSuperAdmin(permissions.BasePermission):
 

    def has_object_permission(self, request, view, obj):
        # Check if the user is trying to edit/cancel their own leave
        if obj.employee == request.user:
            return True

        if request.user.is_superuser:
            return True
        
        return False
    
    
class IsUnitHeadRecommend(permissions.BasePermission):
    """
    Custom permission to allow only the head of a unit to recommend leave
    for users in the same unit.
    """

    def has_permission(self, request, view):
        # Only allow PATCH or PUT (for recommending)
        return request.user.is_authenticated and request.method in ['PATCH', 'PUT']

    def has_object_permission(self, request, view, obj):
        """
        `obj` is the LeaveRequest instance.
        The request.user must be:
        - a head of unit
        - and in the same unit as the applicant
        """
        user = request.user

        return (
            user.is_unit_head and
            obj.employee.unit == user.unit
        )
        
class IsHodOrManager(permissions.BasePermission):
    """
    Custom permission to allow only the head of department to approve leave
    for users in the same department.
    """

    def has_permission(self, request, view):
        # Only allow PATCH or PUT (for recommending)
        return request.user.is_authenticated and request.method in ['PATCH', 'PUT']

    def has_object_permission(self, request, view, obj):
        """
        `obj` is the LeaveRequest instance.
        The request.user must be:
        - a head of department or manager
        - and in the same department as the applicant
        """
        user = request.user

        return (
            user.is_manager and user.is_hod and
            obj.employee.dept == user.dept
        )  
        
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
    
class IsSuperuserDeleteOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only Admins to delete a leave request.
    All other roles can only read (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        # Allow all users to read-only methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow DELETE only if user is authenticated and is admin
        if request.method == "DELETE":
            return request.user.is_authenticated and request.user.is_superuser

        # Disallow all other unsafe methods (e.g., POST, PUT, PATCH)
        return False

class IsAdminOrHROrHOD(permissions.BasePermission):
    """
    Custom permission to allow only:
    - Superusers
    - HR
    - HOD (for their department only)
    - Unit Head (for their unit only)
    to update user profiles.
    """
    def has_permission(self, request, view):
        # Check if user has any of the required roles
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.is_hr or 
             request.user.is_hod or 
             request.user.is_unit_head)
        )

    def has_object_permission(self, request, view, obj):
        # Superusers and HR can update any user
        if request.user.is_superuser or request.user.is_hr:
            return True

        # HOD can only update users in their department
        if request.user.is_hod:
            return obj.dept == request.user.dept

        # Unit Head can only update users in their unit
        if request.user.is_unit_head:
            return obj.unit == request.user.unit

        return False

class CanRegisterUser(permissions.BasePermission):
    """
    Custom permission to allow only:
    - Superusers
    - HR
    - HOD (for their department only)
    - Unit Head (for their unit only)
    to register new users.
    """
    def has_permission(self, request, view):
        # Check if user has any of the required roles
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.is_hr or 
             request.user.is_hod or 
             request.user.is_unit_head)
        )

    def has_object_permission(self, request, view, obj):
        # This method is not used for registration as we're creating new objects
        return True

# custom permission to update own password/username
class CanUpdateOwnCredentials(permissions.BasePermission):
    """
    Custom permission to allow users to update only their own username and password.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is trying to update their own credentials
        return obj.id == request.user.id

class CanUpdateUserPassword(permissions.BasePermission):
    """
    Custom permission to allow only superusers to update any user's password.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser

class CanListUsers(permissions.BasePermission):
    """
    Custom permission to allow only:
    - Superusers
    - HR
    - HOD (can only see users in their department)
    - Unit Head (can only see users in their unit)
    to list users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.is_hr or 
             request.user.is_hod or 
             request.user.is_unit_head)
        )

    def has_object_permission(self, request, view, obj):
        # Superusers and HR can see any user
        if request.user.is_superuser or request.user.is_hr:
            return True

        # HOD can only see users in their department
        if request.user.is_hod:
            return obj.dept == request.user.dept

        # Unit Head can only see users in their unit
        if request.user.is_unit_head:
            return obj.unit == request.user.unit

        return False

class CanManageAccountStatus(permissions.BasePermission):
    """
    Custom permission to allow only:
    - Superusers
    - HR
    - HOD (for their department only)
    - Unit Head (for their unit only)
    to manage account status changes.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or 
             request.user.is_hr or 
             request.user.is_hod or 
             request.user.is_unit_head)
        )

    def has_object_permission(self, request, view, obj):
        # Superusers and HR can manage any user's status
        if request.user.is_superuser or request.user.is_hr:
            return True

        # HOD can only manage users in their department
        if request.user.is_hod:
            return obj.user.dept == request.user.dept

        # Unit Head can only manage users in their unit
        if request.user.is_unit_head:
            return obj.user.unit == request.user.unit

        return False
    
class CanViewOwnAccountStatus(permissions.BasePermission):
    """
    Custom permission to allow users to view only their own account status history.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is trying to view their own status history
        return obj.user == request.user

class CanViewAccountStatusDetail(permissions.BasePermission):
    """
    Custom permission to allow:
    - Superusers
    - HR
    - HOD (for their department only)
    - Unit Head (for their unit only)
    - Users to view their own status history
    to view account status details.
    """
    def has_object_permission(self, request, view, obj):
        # Superusers and HR can view any status history
        if request.user.is_superuser or request.user.is_hr:
            return True

        # HOD can only view status history for users in their department
        if request.user.is_hod:
            return obj.user.dept == request.user.dept

        # Unit Head can only view status history for users in their unit
        if request.user.is_unit_head:
            return obj.user.unit == request.user.unit

        # Users can view their own status history
        return obj.user == request.user

class CanViewLoginHistory(permissions.BasePermission):
    """
    Custom permission to allow:
    - Superusers
    - HR
    - HOD (for their department only)
    - Unit Head (for their unit only)
    - Users to view their own login history
    to view login history.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusers and HR can view any login history
        if request.user.is_superuser or request.user.is_hr:
            return True

        # HOD can only view login history for users in their department
        if request.user.is_hod:
            return obj.user.dept == request.user.dept

        # Unit Head can only view login history for users in their unit
        if request.user.is_unit_head:
            return obj.user.unit == request.user.unit

        # Users can view their own login history
        return obj.user == request.user