import ujson
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from django.forms import model_to_dict

from apps.models import Message, Room


class CustomAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not isinstance(text_data, dict):
            await self.send_json({'message': 'xabar json bolishi shart'})
            return
        return await super().receive(text_data, bytes_data, **kwargs)

    @classmethod
    async def decode_json(cls, text_data):
        return ujson.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return ujson.dumps(content)


class ChatConsumer(CustomAsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None

    async def is_authenticate(self) -> bool:
        if self.user.is_anonymous:
            await self.send_json({'message': 'login is required!'})
            await self.disconnect(0)
            await self.close()
            return False
        return True

    async def connect(self):
        self.user = self.scope['user']
        # connection has to be accepted
        await self.accept()
        if not await self.is_authenticate():
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = await Room.objects.aget(name=self.room_name)
        self.user_inbox = f'inbox_{self.user.id}'

        # # join the room group
        # await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # send the user list to the newly joined user
        # user_list = []
        # async for user in self.room.online.all():
        #     user_list.append(user.username)
        #
        # await self.send_json({
        #     'type': 'user_list',
        #     'users': user_list,
        # })

        # create a user inbox for private messages
        await self.channel_layer.group_add(self.user_inbox, self.channel_name)

        # send the join event to the room
        await self.notify_status()
        # await self.room_update_user(self.room, self.user)

    async def notify_status(self, is_connected: bool = True):
        pass
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'user_join',
        #         'user': model_to_dict(self.user, ('id', 'username')),
        #     }
        # )

    # @sync_to_async
    # def room_update_user(self, room, user, action: str = 'add'):
    #     getattr(room.online, action)(user)

    async def disconnect(self, close_code):
        # delete the user inbox for private messages
        await self.channel_layer.group_discard(self.user_inbox, self.channel_name, )

        # # send the leave event to the room
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'user_leave',
        #         'user': self.user.username,
        #     }
        # )
        # self.room_update_user(self.room, self.user, 'remove')

    async def receive_json(self, content, **kwargs):
        if not (len(set(content) & {'target', 'type'}) > 1):
            await self.send_json({'message': 'xabar yuboriladigan user idni kiriting'})
            return

        if content['type'] == 'private':
            msg = await Message.objects.acreate(user=self.user, room=self.room, text=content['message'])
            # send private message to the target
            await self.channel_layer.group_send(
                f"inbox_{content['target']}",
                {
                    'type': 'private_message',
                    'user': model_to_dict(self.user, ('id', 'username')),
                    'message': model_to_dict(msg, ('id', 'text')),
                }
            )
            # send private message delivered to the user
            await self.send_json({
                'type': 'chat_message',
                'target': content['target'],
                'message': model_to_dict(msg, ('id', 'text')),
            })
            return

        # send chat message event to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': model_to_dict(self.user, ('id', 'username')),
                'message': content['message'],
            }
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def user_join(self, event):
        await self.send_json(event)

    async def user_leave(self, event):
        await self.send_json(event)

    async def private_message(self, event):
        await self.send_json(event)

    async def private_message_delivered(self, event):
        await self.send_json(event)


'''

string1
ws://localhost:8000/ws/chat/p21/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMzI4NzEyLCJpYXQiOjE3MjY5MjIzMTIsImp0aSI6IjkxM2I2OTgwMWU4NjQ0NDg4MGZlZDhlZWNiZDI4ZDQwIiwidXNlcl9pZCI6Mn0.htTAe3EZh5ZKno286tCuyDijBWH-FCGCu3luA2jyaCo


string2
ws://localhost:8000/ws/chat/p21/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMzI4OTIwLCJpYXQiOjE3MjY5MjI1MjAsImp0aSI6IjRhNGJmMTVkZjRjYjRhYjM4Y2Q5ZmIwYmQ0OTk5ODMxIiwidXNlcl9pZCI6M30.hxkXmMl3qmDvwb8oDDEAfq3ft5H_OYr24dfi6V_m_04


string3
ws://localhost:8000/ws/chat/p21/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMzMwMTYxLCJpYXQiOjE3MjY5MjM3NjEsImp0aSI6IjFkYzk2NzhhNGMzZTQ0MmY5NWEzOTE1NTg0NDg2MjdjIiwidXNlcl9pZCI6NH0.LpSO6iDYm8Qz9h0ymcyV_NpFAClPBdmmmmTx_7R_R6Y

'''
