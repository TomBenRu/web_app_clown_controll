from enum import Enum


class AuthorizationTypes(Enum):
    supervisor = 'supervisor'
    admin = 'admin'
    department = 'department'
    actor = 'actor'
