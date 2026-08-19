from fastapi import status

from app.core.exceptions import AppBaseException


class InvalidPasswordException(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Incorrect password."
