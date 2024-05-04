from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseOrder, HistoricalPerformance
from django.db.models import Avg, F

@receiver(post_save, sender=PurchaseOrder)
def update_performance_metrics(sender, instance, created, **kwargs):
    if not created:
        vendor = instance.vendor
        if instance.status == "Completed":
            update_on_time_delivery_rate(vendor)
            update_fulfillment_rate(vendor)
            create_history_performance_metrics(vendor)

            if instance.quality_rating is not None:
                update_quality_rating_avg(vendor)

        if instance.acknowledgment_date is not None:
            update_avg_response_time(vendor)

def update_avg_response_time(vendor):
    art = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False, issue_date__isnull=False).aggregate(avg_response=Avg(F('acknowledgment_date') - F('issue_date')))['avg_response'] or 0
    total_seconds = art.total_seconds()
    vendor.average_response_time = total_seconds
    vendor.save()
    return total_seconds

def update_on_time_delivery_rate(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed')
    total_orders = completed_orders.count()
    on_time_orders = completed_orders.filter(delivery_date__lte=F('acknowledgment_date')).count()
    on_time_delivery_rate = (on_time_orders / total_orders) * 100 if total_orders > 0 else 0
    vendor.on_time_delivery_rate = on_time_delivery_rate
    vendor.save()
    return on_time_delivery_rate

def update_quality_rating_avg(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed', quality_rating__isnull=False)
    quality_rating_avg = completed_orders.aggregate(avg_rating=Avg('quality_rating'))['avg_rating'] or 0
    vendor.quality_rating_avg = quality_rating_avg
    vendor.save()
    return quality_rating_avg

def update_fulfillment_rate(vendor):
    total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
    successful_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed').count()
    fulfillment_rate = (successful_orders / total_orders) * 100 if total_orders > 0 else 0
    vendor.fulfillment_rate = fulfillment_rate
    vendor.save()
    return fulfillment_rate


def create_history_performance_metrics(vendor):
    HistoricalPerformance.objects.create(
        vendor=vendor,
        average_response_time=update_avg_response_time(vendor),
        on_time_delivery_rate=update_on_time_delivery_rate(vendor),
        quality_rating_avg=update_quality_rating_avg(vendor),
        fulfillment_rate=update_avg_response_time(vendor)
    )

    # try:
    #     performance = HistoricalPerformance.objects.filter(vendor=vendor).latest('date')
    #     performance.average_response_time = total_seconds
    #     performance.save()
    # except HistoricalPerformance.DoesNotExist:
    #     HistoricalPerformance.objects.create(
    #         vendor=vendor,
    #         average_response_time=total_seconds
    #     )