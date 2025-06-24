from django.urls import path
from core.api.views import *

urlpatterns = [
    path('depts/', DeptCreateList.as_view(), name='dept-list-create'),
    path('depts/<int:pk>', DeptDetailView.as_view(), name='dept-detail'),
    
    path('units/', UnitCreateList.as_view(), name='unit-list-create'),
    path('units/<int:pk>/', UnitsDetail.as_view(), name='unit-detail'),
    
    path('leave-type/',LeaveTypeCreateList.as_view(),name='leave-type-list-create'),
    path('leave-type/<int:pk>/', LeaveTypeDetail.as_view(),name='leave-type-detail'),
    
    path('holidays/', HolidayCreateList.as_view(), name='holiday-list-create'),
    path('holidays/<int:pk>/', HolidayDetail.as_view(), name='Holiday-detail'),
    
    # TODO
    
    path('leave-request/',CreateLeaveApplication.as_view(), name='leave-app'),
    path('list-leave-request/', ListLeaveRequest.as_view(), name='list-leave-app'),
    path('leave-request-detail/<int:pk>/', LeaveRequestDetail.as_view(),name="leave-request-detail"),
    path('update-leave-request/<int:pk>/', LeaveRequestUpdate.as_view(),name="update-leave-request"),
    path('recommend-leave-request/<int:pk>/', RecommendLeaveRequest.as_view(),name="recommend-leave-request"),
    path('leave-request-approval/<int:pk>/', ApproveRejectLeaveRequest.as_view(),name="leave-request-approval"),
    path('delete-leave-request/<int:pk>/',DeleteLeaveRequest.as_view(),name='delete-leave-request'),
    
    path('leave-requests/search/<str:search>/', LeaveRequestSearch.as_view(), name='leave-request-search'),

    # path('leave-balances/', LeaveBalanceList.as_view(), name='leave-balance-list'),
    
    path('list-dept-leave/<int:pk>/', ListDeptLeaveRequest.as_view(), name='list-dept-leave'),
    path('list-unit-leave/<int:pk>/', ListUnitLeaveRequest.as_view(), name='list-unit-leave'),
    
    path('user-leave/<int:pk>/', ListUserLeaveRequest.as_view(), name="user-leave")
    
    
   
    
    
    # list all leave based on user id
    # list all leave recommended by a given user <provide the user_id>
    # list all leave approved by a given user <provide the user_id>
    
]
