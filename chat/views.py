

from rest_framework.views import View, APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response, SimpleTemplateResponse
from rest_framework import status


from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from . import forms, models, serializers


class Home(View):

    def get(self, request, *args, **kwargs):
        return render(request, "chat/index.html")


class ChatHome(View):

    def get(self, request, room_name):

        return render(request, "chat/room.html", {"room_name": room_name})


class PublicChatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        chatroom = models.ChatRoom.objects.all()

        ser_data = serializers.PublicChatsSerializer(
            instance=chatroom, many=True)

        return Response(ser_data.data, status=status.HTTP_200_OK)


class AdminChatView(View, LoginRequiredMixin):

    form_class = forms.OptionAdminForm

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        return render(request, "chat/index_admin.html", {"forms": form})

    def post(self, request, *args, **kwargs):

        forms = self.form_class(request.POST)

        if forms.is_valid():

            cd = forms.cleaned_data

            admin = cd['admin']
            user = request.user

            return redirect("chat:admin_user_room", admin, user)


class AdminChatRoomView(View):
    def get(self, request, admin, user):
        return render(request, "chat/admin_room.html", {"user": user, "admin": admin})
