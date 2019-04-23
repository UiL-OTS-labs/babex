from enum import Enum


class Event(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    UNCATEGORISED = 'uncategorised'


class UserType(Enum):
    SYSTEM = 'system'
    ADMIN = 'admin'
    LEADER = 'leader'
    PARTICIPANT = 'participant'
