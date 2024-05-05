from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, ViewVendorSerializer, AddVendorSerializer, UpdateVendorSerializer, VendorPerformanceSerializer, PurchaseOrderSerializer, AddPurchaseOrderSerializer, UpdatePurchaseOrderSerializer, HistoricalPerformanceSerializer
from django.utils import timezone
from django.db.models import Avg, F
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import VendorFilter
from .signals import update_avg_response_time
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    http_method_names = ["get", "post", "put", "delete"]
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return Vendor.objects.all()
    #     elif self.request.method == 'GET':
    #         raise PermissionDenied("You do not have permission to access this resource.")
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddVendorSerializer
        elif self.request.method == "PATCH" or self.request.method == "PUT":
            return  UpdateVendorSerializer
        return ViewVendorSerializer
    
    def create(self, request, *args, **kwargs):
        contact_details = request.data.get('contact_details')
        if contact_details and Vendor.objects.filter(contact_details=contact_details).exists():
            return Response({'detail': 'Vendor with these contact details already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Vendor created successfully.'}, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'detail': 'Vendor updated successfully.'}, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Vendor deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    http_method_names = ["get", "post", "put", "delete"]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = VendorFilter
    search_fields = ['vendor__vendor_code']
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddPurchaseOrderSerializer
        elif self.request.method == "PATCH" or self.request.method == "PUT":
            return  UpdatePurchaseOrderSerializer
        return PurchaseOrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'detail': 'Purchase order created successfully.'}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'detail': 'Purchase order updated successfully.'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Purchase order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class AcknowledgePurchaseOrderView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=pk)
            vendor = purchase_order.vendor
        except PurchaseOrder.DoesNotExist:
            return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if purchase_order.acknowledgment_date:
            return Response({'detail': 'Acknowledgment is already done.'}, status=status.HTTP_400_BAD_REQUEST)

        purchase_order.acknowledgment_date = datetime.now()
        purchase_order.save()
        update_avg_response_time(vendor)

        return Response({'detail': 'Acknowledgment successful.'}, status=status.HTTP_200_OK)
    
class VendorPerformanceView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
        except :
            return Response({'detail': 'Vendor not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VendorPerformanceSerializer(vendor)
        return Response(serializer.data)