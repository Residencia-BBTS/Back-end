from ninja import NinjaAPI
from tickets.api import router as tickets_router


api = NinjaAPI()

api.add_router("/tickets", tickets_router)
