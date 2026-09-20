from django.conf import settings
from django.db import models


class Notification(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=40)
    title = models.CharField(max_length=120)
    message = models.TextField()
    entity_type = models.CharField(max_length=40, blank=True)
    entity_id = models.CharField(max_length=64, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    legacy_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient", "is_read", "created_at"], name="notification_recipient_idx")
        ]

    def __str__(self):
        return self.title


class Message(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    legacy_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["sender", "recipient", "created_at"], name="message_conversation_idx")
        ]

    def __str__(self):
        return f"{self.sender} to {self.recipient}"
