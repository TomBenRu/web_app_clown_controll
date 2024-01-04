from typing import Annotated, Any
from uuid import UUID

from pony.orm import db_session

from database import models, schemas


@db_session
def get_schema_of_user(user_db: models.User) -> None | schemas.SuperUser | schemas.Admin | schemas.Department | schemas.Actor:
    if not user_db:
        return None
    elif isinstance(user_db, models.SuperUser):
        return schemas.SuperUser.model_validate(user_db)
    elif isinstance(user_db, models.Admin):
        return schemas.Admin.model_validate(user_db)
    elif isinstance(user_db, models.Department):
        return schemas.Department.model_validate(user_db)
    elif isinstance(user_db, models.Actor):
        return schemas.Actor.model_validate(user_db)
    else:
        raise ValueError("Invalid user_db object type.")


@db_session
def create_superuser(superuser: schemas.SuperUserCreate) -> schemas.SuperUser:
    new_superuser = models.SuperUser(f_name=superuser.f_name,
                                     l_name=superuser.l_name,
                                     username=superuser.username,
                                     password=superuser.password)
    return schemas.SuperUser.model_validate(new_superuser)


class User:

    @staticmethod
    @db_session
    def get(user_id: UUID):
        user_db = models.User.get(id=user_id)
        return get_schema_of_user(user_db)


    @staticmethod
    @db_session
    def get_user_by_username(username: str):
        user_db = models.User.get(username=username)
        return get_schema_of_user(user_db)


class Actor:
    @staticmethod
    @db_session
    def get_all():
        actors_db = models.Actor.select()
        return [schemas.Actor.model_validate(a) for a in actors_db]

    @staticmethod
    @db_session
    def create():
        new_actor = models.Actor(f_name='Thomas', l_name='Ruff', artist_name='Karotte', username='tombenru',
                                 password='Marionetten')
        return schemas.Actor.model_validate(new_actor)


class Admin:
    @staticmethod
    @db_session
    def create_account(user: schemas.ActorCreate | schemas.DepartmentCreate) -> schemas.Actor | schemas.Department:
        if isinstance(user, schemas.ActorCreate):
            new_actor = models.Actor(f_name=user.f_name,
                                     l_name=user.l_name,
                                     artist_name=user.artist_name,
                                     username=user.username,
                                     password=user.password)
            return schemas.Actor.model_validate(new_actor)
        if isinstance(user, schemas.DepartmentCreate):
            location_db = models.Location.get(id=user.location_id)
            new_department = models.Department(name=user.name,
                                               descriptive_name=user.descriptive_name,
                                               location=location_db,
                                               username=user.username,
                                               password=user.password)
            return schemas.Department.model_validate(new_department)

    @staticmethod
    @db_session
    def create_location(location: schemas.LocationCreate) -> schemas.Location:
        new_location = models.Location(name=location.name)
        return schemas.Location.model_validate(new_location)


class SuperUser:
    @staticmethod
    @db_session
    def create_admin(admin: schemas.AdminCreate) -> schemas.Admin:
        new_admin = models.Admin(f_name=admin.f_name,
                                 l_name=admin.l_name,
                                 username=admin.username,
                                 password=admin.password)
        return schemas.Admin.model_validate(new_admin)
