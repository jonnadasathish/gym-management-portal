from django.contrib import admin

from .models import TrainerProfile


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "compensation_model", "compensation_rate", "organization"]
    list_filter = ["compensation_model", "organization"]
    search_fields = ["user__email", "user__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["user"]
