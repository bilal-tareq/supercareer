from django.db import models
from accounts.models import User
from opportunities.models import Job, FreelanceProject


class MatchResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    job = models.ForeignKey(Job, null=True, blank=True, on_delete=models.CASCADE)
    project = models.ForeignKey(FreelanceProject, null=True, blank=True, on_delete=models.CASCADE)

    match_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Match"