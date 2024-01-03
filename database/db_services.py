from uuid import UUID

from pony.orm import db_session

from database import models, schemas


class User:
    @staticmethod
    @db_session
    def get(user_id: UUID) -> schemas.User:
        user_db = models.User.get(id=user_id)
        if not user_db:
            user = None
        elif isinstance(user_db, models.Admin):
            user = schemas.Admin.model_validate(user_db)
        elif isinstance(user_db, models.Department):
            user = schemas.Department.model_validate(user_db)
        elif isinstance(user_db, models.Actor):
            user = schemas.Actor.model_validate(user_db)
        else:
            raise IOError('Fehler in User.get().')

        return user


    @staticmethod
    @db_session
    def get_user_by_username(username: str) -> schemas.User | None:
        user_db = models.User.get(username=username)
        if not user_db:
            user = None
        elif isinstance(user_db, models.Admin):
            user = schemas.Admin.model_validate(user_db)
        elif isinstance(user_db, models.Department):
            user = schemas.Department.model_validate(user_db)
        elif isinstance(user_db, models.Actor):
            user = schemas.Actor.model_validate(user_db)
        else:
            raise IOError('Fehler in User.get().')

        return user


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
