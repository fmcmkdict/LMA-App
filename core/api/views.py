from django.shortcuts import render

# generics view classes
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import generics

# APIView classes
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from .serializers import *

from core.models import *

from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


# using concrete views
class DeptCreateList(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializers

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
    
class LeaveTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializers
