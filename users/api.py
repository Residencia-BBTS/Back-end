from ninja import Router
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from django.contrib.auth import get_user_model
from pydantic import BaseModel

User = get_user_model()
oauth = OAuth()
oauth.register(
   name="microsoft",
   client_id = settings.MICROSOFT_AUTH["client_id"],
   client_secret = settings.MICROSOFT_AUTH["client_secret"],
   authorize_url = settings.MICROSOFT_AUTH["authorize_url"],
   access_token_url = settings.MICROSOFT_AUTH["token_url"],
   client_kwargs={"scope": "openid profile User.Read"}
)

class ConfiguredHttpJwtAuth(BaseModel):
    class Config:
        arbitrary_types_allowed = True

auth_router = Router()

@auth_router.get("/login")
def microsoft_login(request):
    redirect_uri = request.build_absolute_uri("/api/auth/microsoft/callback")
    return redirect(oauth.microsoft.authorize_redirect(request, redirect_uri))
    
@auth_router.get("/microsoft/callback")
def microsoft_callback(request, Auth: ConfiguredHttpJwtAuth):
    try:
        # Tenta obter o token de acesso
        token = oauth.microsoft.authorize_access_token(request)
        user_info = oauth.microsoft.parse_id_token(request, token)

        # Obtém o email do usuário
        email = user_info.get("email")
        if not email:
            return JsonResponse({"error": "Email não encontrado."}, status=400)

        # Cria ou obtém o usuário
        user, created = User.objects.get_or_create(email=email)

        # Cria tokens de acesso e de atualização
        access_token = Auth.create_access_token(identity=user.id)
        refresh_token = Auth.create_refresh_token(identity=user.id)

        # Retorna os tokens em formato JSON
        return JsonResponse({
            "access": access_token,
            "refresh": refresh_token,
        })
    except Exception as e:
        # Retorna um erro caso algo falhe
        return JsonResponse({"error": str(e)}, status=500)