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