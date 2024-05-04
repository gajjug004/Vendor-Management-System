from django_filters.rest_framework import FilterSet
from api.models import PurchaseOrder


class VendorFilter(FilterSet):
    class Meta:
        model = PurchaseOrder
        fields = {
            'vendor__vendor_code': ['exact']
        }