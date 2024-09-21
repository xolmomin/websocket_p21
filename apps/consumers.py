import ujson
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.forms import model_to_dict

from apps.models import Message


class CustomAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):

    @classmethod
    async def decode_json(cls, text_data):
        return ujson.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return ujson.dumps(content)


class ChatConsumer(CustomAsyncJsonWebsocketConsumer):
    group_name = 'chat'

    async def save_msg(self, content) -> Message:
        return await Message.objects.acreate(
            message=content.get('message'),
            author=self.user,
            file_id=content.get('file')
        )

    async def check_user(self) -> bool:
        if self.user.is_anonymous:
            await self.send_json({'msg': 'login is required!'})
            await self.disconnect(0)
            await self.close()
            return False
        return True

    async def notify_status(self, is_connected: bool = True) -> None:
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "notification.message",
                "message": f"{self.user.username} is {('offline', 'online')[is_connected]} !",
                "from_user": model_to_dict(self.user, ['id', 'username']),
            }
        )

    async def connect(self) -> None:
        self.user = self.scope['user']
        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        if not await self.check_user():
            return
        await self.notify_status()

    async def disconnect(self, close_code):
        # Leave room group
        if self.user.is_authenticated:
            await self.notify_status(False)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        keys = {'message', 'file'}
        if len(set(content) & keys) < 1:
            await self.send_json({'message': f'Shu kalitlardan birini yuborish shart {keys}'})
            return

        # Send message to room group
        msg = await self.save_msg(content)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": model_to_dict(msg, ['id', 'message', 'file']),
                "from_user": model_to_dict(self.user, ['id', 'username']),
            }
        )

    async def notification_message(self, event):
        response = {
            "message": event.get('message'),
            "file": event.get('file'),
            "from_user": event["from_user"]['username']
        }
        if self.user.id != event["from_user"]['id']:
            await self.send_json(response)
        else:
            if isinstance(event['message'], dict):
                await self.send_json(event['message'] | {"status": "xabar yuborildi"})

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        response = {
            "message": event["message"]['message'],
            "file": event['message']['file'],
            "from_user": event["from_user"]['username']
        }
        if self.user.id != event["from_user"]['id']:
            await self.send_json(response)
        else:
            if isinstance(event['message'], dict):
                await self.send_json(event['message'] | {"status": "xabar yuborildi"})


'''

ujson +
Botir online bo'ldi +
Botir chiqib ketdi +

required fields +
fayl yuborish + 

1-1


'''
