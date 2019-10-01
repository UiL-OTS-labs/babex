from enum import Enum


class Event(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    UNCATEGORISED = 'uncategorised'
    DOWNLOAD_DATA = 'download_data'
    VIEW_DATA = 'view_data'
    VIEW_SENSITIVE_DATA = 'view_sensitive_data'
    DELETE_DATA = 'delete_data'


class UserType(Enum):
    SYSTEM = 'system'
    ADMIN = 'admin'
    LEADER = 'leader'
    PARTICIPANT = 'participant'
    UNKNOWN = 'unknown'
