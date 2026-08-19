from enum import StrEnum, auto


class ActivityType(StrEnum):
    REGISTRATION = auto()
    LOGIN = auto()
    CHANGE_PASSWORD = auto()
    FORGOT_PASSWORD_INITIATE = auto()
    FORGOT_PASSWORD_COMPLETE = auto()
    ACCOUNT_ACTIVATION = auto()


class ActivityStatus(StrEnum):
    SUCCESS = auto()
    FAILED = auto()
    RATE_LIMITED = auto()
    REQUESTED = auto()
