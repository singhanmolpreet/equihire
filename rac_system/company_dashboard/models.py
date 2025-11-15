from django.db import models
from django.conf import settings

class JobPosting(models.Model):
    """
    Model representing a job posting created by a company.
    """
    #  Use the custom user model.
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of required skills")
    minimum_experience = models.IntegerField(null=True, blank=True,)
    minimum_salary=models.IntegerField(null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        #  Order job postings by creation date in descending order
        ordering = ['-created_at']

