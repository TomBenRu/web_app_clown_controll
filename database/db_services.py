from uuid import UUID

from pony.orm import db_session

from database import models, schemas


class User:
    @staticmethod
    @db_session
    def get_schema_of_user(user_db: models.User) -> None | schemas.Admin | schemas.Department | schemas.Actor:
        if not user_db:
            return None
        elif isinstance(user_db, models.Admin):
            return schemas.Admin.model_validate(user_db)
        elif isinstance(user_db, models.Department):
            return schemas.Department.model_validate(user_db)
        elif isinstance(user_db, models.Actor):
            return schemas.Actor.model_validate(user_db)
        else:
            raise ValueError("Invalid user_db object type.")

    @staticmethod
    @db_session
    def get(user_id: UUID) -> schemas.User:
        user_db = models.User.get(id=user_id)
        return User.get_schema_of_user(user_db)


    @staticmethod
    @db_session
    def get_user_by_username(username: str) -> schemas.User | None:
        user_db = models.User.get(username=username)
        return User.get_schema_of_user(user_db)


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
