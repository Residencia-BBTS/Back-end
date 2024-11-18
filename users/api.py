from ninja import Router
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .schema import SignInSchema, SignUpSchema, AllUsers
from tickets.models import Tickets
from datetime import timedelta

router = Router()

@router.post("/signin")
def signin(request, payload: SignInSchema):
   user = User.objects.get(email=payload.email)
   if user:
      user = authenticate(request, username=user.username, password=user.password)
      return {"message": "Login Successful"}
   else:
      return {"error": "Invalid credentials"}


@router.post("/signup")
def signup(request, user: SignUpSchema):
   user = User(
      username=user.username,
      email=user.email,
      is_staff = user.is_staff
   )
   user.set_password(user.password)
   user.save()

   return {"message": "User created sucessfully!"}


@router.get("/all-users", response=list[AllUsers])
def all_users(request):
   users = User.objects.all()

   user_data = []
   for user in users:
      tickets_atribuidos = Tickets.objects.filter(email=user.email).count()
      tickets_fechados = Tickets.objects.filter(email=user.email, status="Resolved").count()
      resolved_tickets = Tickets.objects.filter(email=user.email, status="Resolved")
      total_resolution_time = timedelta() 

      for ticket in resolved_tickets:
         if ticket.createdTime and ticket.lastModifiedTime:
            resolution_time = ticket.lastModifiedTime - ticket.createdTime
            total_resolution_time += resolution_time

      avg_resolution_time = 0
      if tickets_fechados > 0: 
         avg_resolution_time = total_resolution_time.total_seconds()

      user_info = {
         "username": user.username,
         "email": user.email,
         "tickets_atribuidos": tickets_atribuidos,
         "tickets_fechados": tickets_fechados,
         "is_staff": user.is_staff,
         "avg_resolution_time": avg_resolution_time
      }
      user_data.append(user_info)
   return user_data
