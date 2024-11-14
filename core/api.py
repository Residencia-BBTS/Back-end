from ninja import NinjaAPI
from tickets.api import router as tickets_router
from users.api import router as users_router

api = NinjaAPI()

api.add_router("tickets/", tickets_router)
api.add_router("users/", users_router)