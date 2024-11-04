from ninja import NinjaAPI
from tickets.api import router as tickets_router
from users.api import auth_router 

api = NinjaAPI()

api.add_router("tickets/", tickets_router)
api.add_router("auth/", auth_router)