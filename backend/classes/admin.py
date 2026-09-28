from django.contrib import admin

from .models import Booking, ClassOccurrence, GymClass


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ["name", "branch", "trainer", "capacity", "status"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["branch", "trainer"]


@admin.register(ClassOccurrence)
class ClassOccurrenceAdmin(admin.ModelAdmin):
    list_display = ["gym_class", "start_time", "end_time", "status"]
    list_filter = ["status", "organization"]
    search_fields = ["gym_class__name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["gym_class"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["member", "occurrence", "status", "booked_at"]
    list_filter = ["status", "organization"]
    readonly_fields = ["uuid", "created_at", "updated_at", "booked_at"]
    autocomplete_fields = ["member", "occurrence"]
