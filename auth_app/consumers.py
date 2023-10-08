# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            user_id = self.scope["user"].id
            group_name = f"user_{user_id}"  # Подключите пользователя к его группе веб-сокета
            await self.channel_layer.group_add(group_name, self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        user_id = self.scope["user"].id
        group_name = f"user_{user_id}"
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def notification_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


