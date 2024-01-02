from pony.orm import db_session

from database import models, schemas


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
