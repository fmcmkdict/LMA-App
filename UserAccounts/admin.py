from django.contrib import admin

# Register your models here.
from django.contrib import admin
# import these because of custom user


from django.contrib.auth.admin import UserAdmin
from .models import UserAccounts

# uncomment after checking and editing
class CustomUserAdmin(UserAdmin):
    
    model = UserAccounts
    list_display = ['username']
    
    # fieldsets = (
    #     (None, {
    #         'fields': ('username', 'password')
    #     }),
    #     ('Personal info', {
    #         'fields': ('sur_name','first_name','other_name','dob','gender','phone','class_admitted','session_admitted','admission_number')
    #     }),
    #     ('Permissions', {
    #         'fields': (
    #             'is_active', 'is_staff','is_superuser',
    #             'groups', 'user_permissions'
    #             )
    #     }),
    #     ('Important dates', {
    #         'fields': ('last_login', 'date_joined')
    #     }),
    #     ('Additional info', {
    #         'fields': ('is_student', 'is_teacher',)
    #     })
    # )

    
    


 
admin.site.register(UserAccounts,CustomUserAdmin)
