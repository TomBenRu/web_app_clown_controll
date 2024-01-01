from pony.orm import db_session

from database import models, schemas


class Actor:
    @staticmethod
    @db_session
    def create():
        new_actor = models.Actor(f_name='Thomas', l_name='Ruff', artist_name='Karotte', username='tombenru',
                                 password='Marionetten')
        return schemas.Actor.model_validate(new_actor)
