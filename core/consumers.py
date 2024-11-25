from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Adiciona o WebSocket ao grupo "tickets_group"
        await self.channel_layer.group_add(
            "tickets_group",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove o WebSocket do grupo
        await self.channel_layer.group_discard(
            "tickets_group",
            self.channel_name
        )

    async def new_ticket_notification(self, event):
        # Envia a notificação para o cliente WebSocket
        await self.send(text_data=json.dumps(event["ticket"]))
