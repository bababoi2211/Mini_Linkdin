
from django.db import models
from django.contrib.auth import get_user_model


class ChatRoom(models.Model):
    name = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} room"


class ChatMessage(models.Model):
    room_name = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="room")
    user = models.CharField(max_length=250)
    message = models.CharField()
    timestamp = models.DateTimeField(auto_now_add=True)


class AdminChatRoom(models.Model):

    admin = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="admin")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user")

    message = models.CharField()

    def __str__(self):
        return f"{self.admin} Talk with {self.user}"

    class Meta:
        unique_together = ("admin", "user")


class ChatAdminMessage(models.Model):
    room_name = models.ForeignKey(
        AdminChatRoom, on_delete=models.CASCADE, related_name="admin_room")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    message = models.CharField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    delivered = models.BooleanField(default=True)

    class Meta:
        ordering = ["timestamp"]
