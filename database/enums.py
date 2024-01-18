from enum import Enum


class AuthorizationTypes(Enum):
    superuser = 'superuser'
    admin_of_location = 'admin_of_location'
    admin_of_institution_actors = 'admin_of_institution_actors'
    department = 'department'
    actor = 'actor'
