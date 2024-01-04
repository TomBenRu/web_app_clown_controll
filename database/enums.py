from enum import Enum


class AuthorizationTypes(Enum):
    superuser = 'superuser'
    admin = 'admin'
    department = 'department'
    actor = 'actor'
