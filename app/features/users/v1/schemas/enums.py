from enum import StrEnum, auto


class VerificationTokenType(StrEnum):
    ACCOUNT_ACTIVATION = auto()
    PASSWORD_RESET = auto()


class UserRole(StrEnum):
    ADMIN = auto()
    USER = auto()
