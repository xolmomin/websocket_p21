from pyexpat.errors import messages

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from django.forms import model_to_dict

from apps.models import Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    group_name = 'chat'

    async def save_msg(self, msg: str) -> Message:
        return await Message.objects.acreate(message=msg, author=self.user)

    async def check_user(self) -> None:
        if self.user.is_anonymous:
            await self.send_json({'msg': 'login is required!'})
            await self.disconnect(0)
            await self.close()

    async def notify_status(self, is_connected: bool = True) -> None:
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": f"{self.user.username} is {('offline', 'online')[is_connected]} !",
                "from_user": model_to_dict(self.user, ['id', 'username']),
            }
        )

    async def connect(self) -> None:
        self.user = self.scope['user']
        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.check_user()
        await self.notify_status()

    async def disconnect(self, close_code):
        # Leave room group
        await self.notify_status(False)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        message = content["message"]
        # Send message to room group
        msg = await self.save_msg(message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": model_to_dict(msg, ['id', 'message']),
                "from_user": model_to_dict(self.user, ['id', 'username']),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        msg = event["message"]['message'] if isinstance(event['message'], dict) else event['message']
        response = {
            "message": msg,
            "from_user": event["from_user"]['username']
        }
        if self.user.id != event["from_user"]['id']:
            await self.send_json(response)
        else:
            if isinstance(event['message'], dict):
                await self.send_json(event['message'] | {"status": "xabar yuborildi"})
