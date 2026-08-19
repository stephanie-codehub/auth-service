from enum import StrEnum, auto


class EmailTemplateType(StrEnum):
    ACCOUNT_VERIFICATION = auto()
    PASSWORD_RESET = auto()
    PASSWORD_RESET_CONFIRMATION = auto()
    OTP = auto()
