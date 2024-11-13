from ninja.schema import Schema

class SignUpSchema(Schema):
   username: str
   password: str
   email: str

class SignInSchema(Schema):
   email: str
   password: str