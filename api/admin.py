from django.contrib import admin
from .models import *

# admin.site.register(Vendor)
# admin.site.register(PurchaseOrder)
# admin.site.register(HistoricalPerformance)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name','contact_details','address','vendor_code']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number','vendor','order_date','delivery_date','items','quantity','status','quality_rating','issue_date','acknowledgment_date']

@admin.register(HistoricalPerformance)
class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = ['vendor','date','on_time_delivery_rate','quality_rating_avg','average_response_time','fulfillment_rate']