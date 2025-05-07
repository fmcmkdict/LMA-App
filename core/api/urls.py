from django.urls import path
from core.api.views import *

urlpatterns = [
    path('depts/', DeptCreateList.as_view(), name='dept-list-create'),
    path('depts/<int:pk>', DeptDetailView.as_view(), name='dept-detail'),
    
    path('units/', UnitCreateList.as_view(), name='unit-list-create'),
    path('units/<int:pk>', UnitsDetail.as_view(), name='unit-detail'),
    
    path('leave-type/',LeaveTypeCreateList.as_view(),name='leave-type-list-create'),
    path('leave-type/<int:pk>',LeaveTypeDetail.as_view(),name='leave-type-detail')
]
