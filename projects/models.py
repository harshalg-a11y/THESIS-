from django.db import models
from accounts.models import User


class ThesisRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("in_progress", "In Progress"),
        ("review", "Review"),
        ("delivered", "Delivered"),
    ]
    client = models.ForeignKey(User, related_name="client_requests", on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name="writer_requests", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Milestone(models.Model):
    request = models.ForeignKey(ThesisRequest, related_name="milestones", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)


class Attachment(models.Model):
    request = models.ForeignKey(ThesisRequest, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
