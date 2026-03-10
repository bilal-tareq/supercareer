from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    source_platform = models.CharField(max_length=255)
    source_url = models.URLField()

    posted_date = models.DateField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FreelanceProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)

    platform_name = models.CharField(max_length=255)
    source_url = models.URLField()

    posted_date = models.DateField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title