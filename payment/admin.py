from django.contrib import admin
from django.contrib.admin import ModelAdmin

from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    pass
