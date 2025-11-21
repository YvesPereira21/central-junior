import time
import jwt
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)

            token_jti = token.get('jti')
            token_expiration = token.get('exp')

            get_seconds = int(time.time())
            expires_in = token_expiration - get_seconds

            if expires_in > 0:
                cache.set(f"blacklist: {token_jti}", True, timeout=expires_in)
                return Response({"message": "Logout realizado com sucesso!"}, status=status.HTTP_204_NO_CONTENT)

        except TokenError as e:
            return Response({"erro": f"Token inválido: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token_payload = jwt.decode(refresh_token, options={"verify_signature": False})
                jti = token_payload.get('jti')
                if cache.get(f"blacklist: {jti}"):
                    raise InvalidToken("Erro de autenticação")

            except jwt.exceptions.DecodeError as e:
                raise InvalidToken("Token mal formatado")
            except InvalidToken as e:
                raise e

        return super().post(request,*args, **kwargs)
