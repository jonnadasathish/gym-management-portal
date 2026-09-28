"""Celery wrappers for in-app reminder scans. Tests call the service functions directly."""

from celery import shared_task

from notifications.services import (
    emit_birthday_reminders,
    emit_class_reminders,
    emit_membership_expired_reminders,
    emit_membership_expiring_reminders,
    emit_pt_reminders,
)


@shared_task
def emit_membership_expiring_reminders_task():
    emit_membership_expiring_reminders()


@shared_task
def emit_class_reminders_task():
    emit_class_reminders()


@shared_task
def emit_pt_reminders_task():
    emit_pt_reminders()


@shared_task
def emit_membership_expired_reminders_task():
    emit_membership_expired_reminders()


@shared_task
def emit_birthday_reminders_task():
    emit_birthday_reminders()
