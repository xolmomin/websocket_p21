import ujson

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User


class CustomAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):

    @classmethod
    async def decode_json(cls, text_data):
        return ujson.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return ujson.dumps(content)


class ChatConsumer(CustomAsyncJsonWebsocketConsumer):
    async def get_users(self, n):
        print(1234)
        return await User.objects.acount()

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket

    async def receive_json(self, content, **kwargs):
        message = content["message"]
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]
    #
    #     # Send message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name, {"type": "chat.message", "message": message}
    #     )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        # user_count = User.objects.count()
        user_count = await self.get_users(123)
        response = {
            "message": message,
            "status": "hammasi joyida",
            "data": f"Userlar soni {user_count}"
        }
        await self.send_json(response)


'''
group, channel_layer


1 - 1 yozish (DB)

'''