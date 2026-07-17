import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

print("="*50)
print("CONSUMERS.PY IS BEING LOADED")
print("="*50)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"Connect method called for room: {self.scope['url_route']['kwargs']['room_name']}")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print("Connection accepted")
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to chat room: {self.room_name}',
            'username': 'Test User'
        }))

    async def disconnect(self, close_code):
        print(f"Disconnect called with code: {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username', 'User')
        timestamp = text_data_json.get('timestamp', '')
        
        print(f"Received message from {username}: {message}")
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))