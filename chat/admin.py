from django.contrib import admin

from . import models


admin.site.register(models.ChatMessage)
admin.site.register(models.ChatRoom)
admin.site.register(models.ChatAdminMessage)
admin.site.register(models.AdminChatRoom)
