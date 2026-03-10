from django.db import models
from accounts.models import User


class ScrapingLog(models.Model):
    source_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    details = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class AdminActivity(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="targeted_users"
    )

    created_at = models.DateTimeField(auto_now_add=True)