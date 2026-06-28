import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Kiểm tra user đã đăng nhập
        if self.user.is_anonymous:
            await self.close()
            return

        # Kiểm tra user có quyền vào phòng này không
        is_member = await self.is_user_member(self.room_id, self.user.id)
        if not is_member:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', 'send_message')
        
        if action == 'send_message':
            content = data.get('content', '').strip()
            if content:
                # Lưu tin nhắn vào DB
                message = await self.save_message(self.room_id, self.user.id, content)
                
                # Broadcast tin nhắn đến tất cả trong group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': message.id,
                            'sender': self.user.username,
                            'sender_id': self.user.id,
                            'content': message.content,
                            'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M'),
                            'is_read': message.is_read
                        }
                    }
                )

        elif action == 'mark_read':
            # Đánh dấu tất cả tin nhắn trong phòng đã đọc
            await self.mark_messages_read(self.room_id, self.user.id)

    async def chat_message(self, event):
        # Gửi tin nhắn đến WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))

    @database_sync_to_async
    def is_user_member(self, room_id, user_id):
        """Kiểm tra user có trong phòng chat này không"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.members.filter(id=user_id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room_id, user_id, content):
        """Lưu tin nhắn vào database"""
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(
            room=room,
            sender=user,
            content=content
        )
        return message

    @database_sync_to_async
    def mark_messages_read(self, room_id, user_id):
        """Đánh dấu tất cả tin nhắn trong phòng đã đọc"""
        Message.objects.filter(
            room_id=room_id
        ).exclude(
            sender_id=user_id
        ).update(is_read=True)