

from django.urls import path
from . import views


app_name = "chat"


urlpatterns = [
    path("", views.Home.as_view()),
    path("public-chats/", views.PublicChatsView.as_view()),
    path("<str:room_name>/", views.ChatHome.as_view(), name="room"),
    path("support", views.AdminChatView.as_view(), name="admin_room"),
    path("support/<str:admin>/<str:user>",
         views.AdminChatRoomView.as_view(), name="admin_user_room")

]
