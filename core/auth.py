import requests
import jwt
from jwt import PyJWKClient
from ninja.security import HttpBearer
from django.conf import settings
from django.core.exceptions import PermissionDenied

class AzureBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Carregar as chaves de validação do Azure AD
            jwks_client = PyJWKClient(settings.AZURE_AD_JWKS_URL)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            # Decodificar e validar o token JWT
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.AZURE_AD_CLIENT_ID,
                issuer=settings.AZURE_AD_ISSUER
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise PermissionDenied("Token has expired")
        except jwt.InvalidTokenError:
            raise PermissionDenied("Invalid token")

azure_bearer = AzureBearer()
