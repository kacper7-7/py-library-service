from django.contrib import admin
from django.contrib.admin import ModelAdmin

from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(ModelAdmin):
    list_display = ["id", "user", "book__title"]
