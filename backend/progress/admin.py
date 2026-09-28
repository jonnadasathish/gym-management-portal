from django.contrib import admin

from .models import PersonalBest, ProgressEntry


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ["member", "recorded_at", "weight_kg", "height_cm", "body_fat_pct"]
    list_filter = ["organization"]
    search_fields = ["member__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member"]


@admin.register(PersonalBest)
class PersonalBestAdmin(admin.ModelAdmin):
    list_display = ["member", "exercise_name", "value", "unit", "achieved_at"]
    list_filter = ["organization"]
    search_fields = ["exercise_name", "member__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member"]
