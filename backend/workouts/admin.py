from django.contrib import admin

from .models import Exercise, WorkoutDay, WorkoutDayExercise, WorkoutLog, WorkoutProgram


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "muscle_group", "equipment", "organization"]
    list_filter = ["organization"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]


@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "member", "trainer", "status", "start_date"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "trainer"]


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ["program", "day_index", "label"]
    list_filter = ["organization"]
    search_fields = ["label", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["program"]


@admin.register(WorkoutDayExercise)
class WorkoutDayExerciseAdmin(admin.ModelAdmin):
    list_display = ["workout_day", "exercise", "target_sets", "target_reps", "order"]
    list_filter = ["organization"]
    search_fields = ["uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["workout_day", "exercise"]


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ["member", "exercise", "performed_on", "sets", "reps"]
    list_filter = ["organization"]
    search_fields = ["member__full_name", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    autocomplete_fields = ["member", "exercise", "workout_day_exercise"]
