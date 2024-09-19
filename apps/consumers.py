from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from django.forms import model_to_dict


class ChatConsumer(AsyncJsonWebsocketConsumer):
    group_name = 'chat'

    async def check_user(self) -> None:
        if self.user.is_anonymous:
            await self.send_json({'msg': 'login is required!'})
            await self.disconnect(0)
            await self.close()

    async def connect(self) -> None:
        self.user = self.scope['user']
        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.check_user()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        message = content["message"]
        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": message,
                "from_user": model_to_dict(self.user, ['id', 'username']),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        response = {
            "message": message,
            "from_user": event["from_user"]['username']
        }
        if self.user.id != event["from_user"]['id']:
            await self.send_json(response)
        else:
            await self.send_json({'message': "xabar yetib bordi"})


'''
vaqt + db id
status

'''