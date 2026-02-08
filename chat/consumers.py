

from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from smtplib import SMTPResponseException


from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async

from asgiref.sync import sync_to_async, async_to_sync

import json
import logging
import asyncio
import datetime
import utils
from redis.asyncio import Redis


from .models import ChatMessage, ChatRoom, AdminChatRoom, ChatAdminMessage

logging.basicConfig(filename="chat.log", level=logging.DEBUG,
                    force=True, filemode="w+")


class LocalChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        logging.info("Entered connect method")

        self.room_name = self.scope["url_route"]["kwargs"]['room_name']
        self.group_name = f"chat_{self.room_name}"

        logging.info(
            f"room_name:{self.room_name}, group name:{self.group_name}")

        
        await self.channel_layer.group_add(
            self.group_name, self.channel_name)

        if not self.scope.get('user').is_authenticated:

            await self.close(code=4001, reason="Not S=AUthenticated")

            return

        logging.info(f"group detail {self.groups}")
        chat_room, created = await sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)

        self.chat_room_obj = chat_room

        await self.accept()

        messages = await sync_to_async(list)(ChatMessage.objects.filter(
            room_name=chat_room).order_by("timestamp"))[:20]

        for msg in reversed(messages):
            logging.info(f"message content{msg}")
            await self.send(text_data=json.dumps(
                {
                    "user": msg.user,
                    "message": msg.message,
                    # "timestamp": msg.timestamp.isoformat()
                    "timestamp": msg.timestamp.strftime("%H:%M:%S"),
                }
            ))

    async def disconnect(self, code):
        # await self.send({"message": "Disconnected"})

        await (self.channel_layer.group_discard)(
            self.group_name, self.channel_name)
        


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        user = self.scope["user"]

        await self.create_message(self.chat_room_obj, user, message)

        logging.debug("saving Chat message")

        await (self.channel_layer.group_send)(
            self.group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):

        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def create_message(self, room, user, message):
        return ChatMessage.objects.create(room_name=room, user=user, message=message)

    @database_sync_to_async
    def chat_filter(self, lookup):
        return sync_to_async(ChatMessage.objects.filter(room_name=lookup).order_by("timestamp")[:20])


# Read function
# After Successfully helping the authenticated user close the websocket


class AdminChatConsumer(AsyncWebsocketConsumer):
    async def accept(self, subprotocol=None, headers=None):
        redis = Redis
        self.redis = await redis.from_url("redis://127.0.0.1:6379")

        return await super().accept(subprotocol, headers)

    async def connect(self):

        self.admin_str = self.scope["url_route"]["kwargs"]["admin"]
        self.admin = self.scope["url_route"]["kwargs"]["admin"].split("-")[0]
        self.user = self.scope["url_route"]["kwargs"]["user"]
        self.user_username = self.user.split("-")[0]
        self.group_name = f"chat_{self.user}_admin_{self.admin}"

        # If The are not the Real users
        if self.scope["user"].__str__() != self.user and self.scope["user"].__str__() != self.admin_str:
            logging.debug("logging out the user")
            self.scope["user"].__str__()

            await self.close()
            return

        admin_check = await self.check_admin(self.admin)

        self.admin_obj = admin_check

        self.user_obj = await sync_to_async(get_user_model().objects.get)(username=self.user_username)

        self.chat_room, created = await sync_to_async(AdminChatRoom.objects.get_or_create)(
            admin=self.admin_obj,
            user=self.user_obj)

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        if self.admin == self.user:

            logging.info("sending activation message")

            await self.channel_layer.group_send(
                self.group_name,
                {"type": "status_message", "message": f"✅ Admin {self.admin} is online!"}
            )

        elif self.scope['user'].username == self.admin:

            await self.channel_layer.group_send(
                self.group_name,
                {"type": "status.message",
                    "message": f"✅ Admin {self.admin} is online and Active in The Chat!"}
            )

        else:
            key = f"email_sent:{self.admin}"

            count = await self.redis.get(key)
            count = int(count) if count else 0

            await self.redis.expire(key, 500)

            if count < 2:

                try:

                    await sync_to_async(utils.send_reminder_email)(
                        self.admin_obj.email, f"{settings.HOST}chat/support/{self.admin_str}/{self.user_obj.__str__()}", datetime.datetime.now().isoformat())

                    await self.redis.incr(key)
                except SMTPResponseException:

                    await self.send(
                        json.dumps(
                            {"message": "Error in Email Reminder"}
                        )
                    )

            # elif count >= 2:
            #     await asyncio.sleep(300)
            #     await redis.set(key,0)

        await self.send(
            json.dumps(
                {
                    'user': "Chat Bot",
                    "message": f"Welcome {self.user} your support {self.admin} will be here. ",
                    "timestamp": datetime.datetime.now().isoformat(),

                }
            )
        )

        self.chat_room, created = await sync_to_async(AdminChatRoom.objects.get_or_create)(admin=self.admin_obj, user=self.user_obj)

        # Faster the other option Because of the foreign key we use select_Related
        messages = await sync_to_async(list)(ChatAdminMessage.objects.filter(
            room_name=self.chat_room).select_related("user").order_by("timestamp")[:20])

        for msg in messages:

            await self.send(text_data=json.dumps(

                {

                    "user": f"{msg.user.username}",
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_id": msg.id,
                    "delivered": msg.delivered,
                    "read": msg.read

                    # "timestamp": msg.timestamp.strftime("%H:%M:%S")

                }
            ))

    async def receive(self, text_data=None, bytes_data=None):

        try:
            data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data_json.get("type")

        if msg_type == "read_receipt":

            message_id = data_json.get("message_id")
            if not message_id:
                return

            msg = await self.get_message(message_id)

            logging.info(f"message_id {message_id}")
            if msg.user_id == self.scope["user"].id:
                return

            await self.mark_read(message_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "seen_event",
                    "message_id": message_id
                }
            )

        elif msg_type == "delivered_receipt":

            await self.mark_delivered(message_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "deliver_event",
                    "message_id": message_id
                }
            )
            print(f"no message id {data_json}")

        message = data_json.get("message")
        if message:

            if message == "cls" and self.scope["user"].is_admin:
                await self.delete_admin_chat(self.chat_room)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "system_message",
                        "message": "Chat cleared by admin"
                    }
                )
                return

            user = self.scope["user"]

            message_id = await self.create_admin_chat(self.chat_room, user, message)

            await (self.channel_layer.group_send)(
                self.group_name,
                {"type": "chat.message",
                 "user": user.get_username(),
                 'time_stamp': data_json["timestamp"],
                 "message": message,
                 "message_id": message_id
                 }
            )
            await self.mark_delivered(message_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "deliver_event",
                    "message_id": message_id
                }
            )

    @database_sync_to_async
    def check_admin(self, admin):

        try:

            logging.info(f"admin in func {admin}")
            logging.info(f"admin in func {type(admin)}")

            admin = get_user_model().objects.get(username=admin)

            return admin if admin.is_admin else False

        except get_user_model().DoesNotExist:
            logging.info("admin Doesnt Exist")
            self.close(code=4002, reason="Admin Doesnt Exist")

    @database_sync_to_async
    def create_admin_chat(self, room_name, user, message):

        if not message == "cls":

            chat_obj = ChatAdminMessage.objects.create(
                room_name=room_name, user=user, message=message)
            return chat_obj.id

    @database_sync_to_async
    def delete_admin_chat(self, room_name):
        return ChatAdminMessage.objects.filter(room_name=room_name).delete(

        )

    @database_sync_to_async
    def mark_read(self, message_id):
        ChatAdminMessage.objects.filter(id=message_id).update(read=True)

    @database_sync_to_async
    def mark_delivered(self, message_id):
        ChatAdminMessage.objects.filter(id=message_id).update(delivered=True)

    async def seen_event(self, event):
        await self.send(json.dumps({
            "type": "read_receipt",
            "message_id": event["message_id"]
        }))

    async def deliver_event(self, event):

        await self.send(json.dumps({
            "type": "delivered_receipt",
            "message_id": event["message_id"]
        }))

    @database_sync_to_async
    def get_message(self, message_id):
        return ChatAdminMessage.objects.get(id=message_id)

    async def chat_message(self, event):

        message = event["message"]
        user = event["user"]
        message_id = event["message_id"]
        await self.send(text_data=json.dumps(
            {
                "type": "sent_receipt",
                "message": message,
                "user": user,
                "timestamp": event["time_stamp"],
                "message_id": message_id
            })
        )

    async def disconnect(self, code):

        await (self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat.delete",
                "message": "The chat Will be soon deleted",
                "group_name": self.chat_room
            }
        )

        await (self.channel_layer.group_discard)(self.group_name, self.channel_name)

    async def status_message(self, event):
        await self.send(text_data=json.dumps({
            "user": "System",
            "message": event["message"]
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            "user": "System",
            "message": event["message"]
        }))

    async def chat_delete(self, event):

        await asyncio.sleep(10)
        group_name = event["group_name"]
        self.delete_admin_chat(group_name)
        await self.send(
            json.dumps(
                {
                    "user": "Systme",
                    "message": f"{event["message"]}"
                }
            )
        )
