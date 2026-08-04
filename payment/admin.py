from django.contrib import admin
from django.contrib.admin import ModelAdmin

from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ["id", "borrowing", "status", "type", "money_to_pay"]
    list_filter = ["status", "type"]
