from django.urls import path
from core import TicketConsumer

websocket_urlpatterns = [
    path("ws/tickets/", TicketConsumer.as_asgi()),
]
