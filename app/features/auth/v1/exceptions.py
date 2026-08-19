from fastapi import status

from app.core.exceptions import AppBaseException, HTMLException


class InvalidCredentialsError(AppBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Incorrect email or password."


class InvalidAccountTokenException(HTMLException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid or expired token"


class UnverifiedAccountException(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Activate your account to login"
