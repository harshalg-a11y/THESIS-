from django.db import models
from accounts.models import User


class Thread(models.Model):
    client = models.ForeignKey(User, related_name="client_threads", on_delete=models.CASCADE)
    writer = models.ForeignKey(User, related_name="writer_threads", on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)

    def __str__(self):
        return self.subject


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
