from ninja import Router
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .schema import SignInSchema, SignUpSchema

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
      email=user.email
   )
   user.set_password(user.password)
   user.save()

   return {"message": "User created sucessfully!"}