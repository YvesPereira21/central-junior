from rest_framework.exceptions import APIException
from rest_framework import status


class AnswerAlreadyAccepted(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Essa resposta já foi aceita.'
    default_code = 'conflito'

class InvalidData(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Data inválida.'
    default_code = 'inválida'

class ObjectNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Objeto não encontrado'
    default_code = 'inexistente'
