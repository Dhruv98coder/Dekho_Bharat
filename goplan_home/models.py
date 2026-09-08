from django.conf import settings
from django.db import models


class TripRecord(models.Model):
    """A small Django-only travel history record for the current user/session."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    title = models.CharField(max_length=180)
    origin = models.CharField(max_length=180, blank=True)
    destination = models.CharField(max_length=180)
    mode = models.CharField(max_length=30, default="car")
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title