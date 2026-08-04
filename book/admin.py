from django.contrib import admin
from django.contrib.admin import ModelAdmin

from book.models import Book


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ["id", "title", "author", "cover", "inventory", "daily_fee"]
    list_filter = ["cover"]
    search_fields = ["title", "author"]
    list_display_links = ["id", "title"]
