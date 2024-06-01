import datetime
import json
import sys
from typing import Annotated, Any
from uuid import UUID

from pony.orm import db_session

from database import models, schemas


@db_session
def get_schema_of_user(user_db: models.User) -> None | schemas.SuperUser | schemas.PersonShow | schemas.Department | schemas.ActorShow:
    if not user_db:
        return None
    elif isinstance(user_db, models.SuperUser):
        return schemas.SuperUser.model_validate(user_db)
    elif isinstance(user_db, models.Department):
        return schemas.Department.model_validate(user_db)
    elif isinstance(user_db, models.Actor):
        return schemas.ActorShow.model_validate(user_db)
    elif isinstance(user_db, models.Person):
        return schemas.PersonShow.model_validate(user_db)
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
    def get(actor_id: UUID) -> schemas.ActorShow:
        actor_db = models.Actor.get(id=actor_id)
        return schemas.ActorShow.model_validate(actor_db)

    @staticmethod
    @db_session
    def get_all_actors() -> list[schemas.ActorShow]:
        actors_db = models.Actor.select()
        return [schemas.ActorShow.model_validate(a) for a in actors_db]

    @staticmethod
    @db_session
    def get_all_actors_of_institution_actors(institution_actors_id: UUID) -> list[schemas.ActorShow]:
        institution_actors_db = models.InstitutionActors.get(id=institution_actors_id)
        actors_db = models.Actor.select(institution_actors=institution_actors_db)
        return [schemas.ActorShow.model_validate(a) for a in actors_db]

    @staticmethod
    @db_session
    def get_all_available_actors_of_institution_actors(institution_actors_id: UUID) -> list[schemas.ActorShow]:
        institution_actors_db = models.InstitutionActors.get(id=institution_actors_id)
        actors_db = models.Actor.select(institution_actors=institution_actors_db, team_of_actors=None)
        return [schemas.ActorShow.model_validate(a) for a in actors_db]

    @staticmethod
    @db_session
    def get_all_locations() -> list[schemas.LocationShow]:
        locations_db = models.Location.select()
        return [schemas.LocationShow.model_validate(l) for l in locations_db]

    @staticmethod
    @db_session
    def get_all_locations_of_institution_actors(institution_actors_id: UUID) -> list[schemas.LocationShow]:
        institution_actors_db = models.InstitutionActors.get(id=institution_actors_id)
        locations_db = models.Location.select(institution_actors=institution_actors_db)
        return [schemas.LocationShow.model_validate(l) for l in locations_db]

    @staticmethod
    @db_session
    def get_all_departments_of_location(location_id) -> list[schemas.DepartmentShow]:
        location_db = models.Location.get(id=location_id)
        departments_db = models.Department.select(location=location_db)
        return [schemas.DepartmentShow.model_validate(d) for d in departments_db]

    @staticmethod
    @db_session
    def create_team_of_actors(new_team: schemas.TeamOfActorsCreate) -> schemas.TeamOfActorsShow:
        location_db = models.Location.get(id=new_team.location_id)
        actors_db = [models.Actor.get(id=a) for a in new_team.actor_ids]
        if new_team.id:
            new_team_db = models.TeamOfActors(id=new_team.id, location=location_db, actors=actors_db)
        else:
            new_team_db = models.TeamOfActors(location=location_db, actors=actors_db)
        return schemas.TeamOfActorsShow.model_validate(new_team_db)

    @staticmethod
    @db_session
    def delete_team_of_actors(team_id: UUID):
        team_db = models.TeamOfActors.get(id=team_id)
        team_db.delete()

    @staticmethod
    @db_session
    def get_team_of_actors(team_of_actors_id: UUID) -> schemas.TeamOfActorsShow | None:
        team_of_actors_db = models.TeamOfActors.get(id=team_of_actors_id)
        return schemas.TeamOfActorsShow.model_validate(team_of_actors_db) if team_of_actors_db else None

    @staticmethod
    @db_session
    def get_all_teams_of_actors(location_id: UUID) -> list[schemas.TeamOfActorsShow]:
        location_db = models.Location.get(id=location_id)
        teams_db = models.TeamOfActors.select(location=location_db)
        return [schemas.TeamOfActorsShow.model_validate(t) for t in teams_db]

    @staticmethod
    @db_session
    def get_all_session_messages_of_team_of_actors(team_of_actors_id: UUID,
                                                   unsent: bool) -> list[schemas.SessionMessageShow]:
        team_of_actors_db = models.TeamOfActors.get(id=team_of_actors_id)
        print(f'................................ {team_of_actors_db=}', flush=True)
        if unsent:
            print('............................ in unsent')
            session_messages_db = (models.SessionMessage
                                   .select(team_of_actors=team_of_actors_db, sent=None)
                                   .order_by(lambda sm: sm.created_at))
            print(f'.................................{session_messages_db=}', flush=True)
        else:
            session_messages_db = (models.SessionMessage
                                   .select(team_of_actors=team_of_actors_db)
                                   .order_by(lambda sm: sm.created_at))

        return [schemas.SessionMessageShow.model_validate(sm) for sm in session_messages_db]

    @staticmethod
    @db_session
    def create_session_message(session_message: schemas.SessionMessageCreate) -> schemas.SessionMessageShow:
        team_of_actors_db = models.TeamOfActors.get(id=session_message.team_of_actors_id)
        message_id = UUID(json.loads(session_message.message)['message_id'])
        session_message_db = models.SessionMessage(id=message_id,
                                                   team_of_actors=team_of_actors_db,
                                                   message=session_message.message,
                                                   sent=None)
        return schemas.SessionMessageShow.model_validate(session_message_db)

    @staticmethod
    @db_session
    def set_session_message_as_sent(session_message_id: UUID) -> schemas.SessionMessageShow | None:
        session_message_db = models.SessionMessage.get_for_update(id=session_message_id)
        if session_message_db:
            session_message_db.sent = datetime.datetime.now(datetime.timezone.utc)
        else:
            print('............................. keine entsprechende Message in db')
        return schemas.SessionMessageShow.model_validate(session_message_db) if session_message_db else None

    @staticmethod
    @db_session
    def set_all_messages_to_unsent(team_of_actors_id: UUID):
        team_of_actors_db = models.TeamOfActors.get(id=team_of_actors_id)
        for session_message in team_of_actors_db.session_messages:
            session_message.sent = None



class Department:
    @staticmethod
    @db_session
    def get(department_id: UUID) -> schemas.DepartmentShow:
        department_db = models.Department.get(id=department_id)
        return schemas.DepartmentShow.model_validate(department_db)


class Admin:
    @staticmethod
    @db_session
    def create_account(
            user: schemas.ActorCreate | schemas.DepartmentCreate, user_id: UUID | None = None) -> schemas.Actor | schemas.Department:
        if isinstance(user, schemas.ActorCreate):
            institution_actors_db = models.InstitutionActors.get(id=user.institution_actors_id)
            if user_id:
                new_actor = models.Actor(id=user_id,
                                         f_name=user.f_name,
                                         l_name=user.l_name,
                                         artist_name=user.artist_name,
                                         username=user.username,
                                         password=user.password,
                                         institution_actors=institution_actors_db)
            else:
                new_actor = models.Actor(f_name=user.f_name,
                                         l_name=user.l_name,
                                         artist_name=user.artist_name,
                                         username=user.username,
                                         password=user.password,
                                         institution_actors=institution_actors_db)

            return schemas.Actor.model_validate(new_actor)
        if isinstance(user, schemas.DepartmentCreate):
            location_db = models.Location.get(id=user.location_id)
            if user_id:
                new_department = models.Department(id=user_id,
                                                   name=user.name,
                                                   descriptive_name=user.descriptive_name,
                                                   location=location_db,
                                                   username=user.username,
                                                   password=user.password)
            else:
                new_department = models.Department(name=user.name,
                                                   descriptive_name=user.descriptive_name,
                                                   location=location_db,
                                                   username=user.username,
                                                   password=user.password)

            return schemas.Department.model_validate(new_department)

    @staticmethod
    @db_session
    def delete_account(user: schemas.Department | schemas.Actor):
        user_db = (models.Department.get_for_update(id=user.id) if isinstance(user, schemas.Department)
                   else models.Actor.get_for_update(id=user.id))
        user_db.delete()

    @staticmethod
    @db_session
    def create_department(department: schemas.DepartmentCreate, department_id: UUID = None) -> schemas.Department:
        location_db = models.Location.get(id=department.location_id)
        new_department = (models.Department(id=department_id,
                                            name=department.name,
                                            username=department.username,
                                            password=department.password,
                                            descriptive_name=department.descriptive_name,
                                            location=location_db) if department_id
                          else models.Department(name=department.name,
                                                 username=department.username,
                                                 password=department.password,
                                                 descriptive_name=department.descriptive_name,
                                                 location=location_db))
        return schemas.Department.model_validate(new_department)

    @staticmethod
    @db_session
    def delete_department(department_id: UUID):
        department_db = models.Department.get_for_update(id=UUID)
        department_db.delete()


class SuperUser:
    @staticmethod
    @db_session
    def create_person(admin: schemas.PersonCreate) -> schemas.PersonShow:
        location_of_admin_db = (models.Location.get(id=admin.location_of_admin_id)
                                if admin.location_of_admin_id else None)
        institution_actors_of_admin_db = (models.InstitutionActors.get(id=admin.institution_actors_of_admin_id)
                                          if admin.institution_actors_of_admin_id else None)
        exclusions = {'location_of_admin_id', 'institution_actors_of_admin_id'}
        if not admin.id:
            exclusions.add('id')
        new_admin = models.Person(**admin.model_dump(exclude=exclusions))
        new_admin.location_of_admin = location_of_admin_db
        new_admin.institution_actors_of_admin = institution_actors_of_admin_db

        return schemas.PersonShow.model_validate(new_admin)

    @staticmethod
    @db_session
    def delete_person(admin_id: UUID):
        admin_db = models.Person.get_for_update(id=admin_id)
        admin_db.delete()

    @staticmethod
    @db_session
    def create_institution_actors(institution_actors: schemas.InstitutionActorsCreate) -> schemas.InstitutionActorsShow:
        admin_db = models.Person.get(id=institution_actors.admin_id)
        institution_db = models.InstitutionActors(name=institution_actors.name, admin=admin_db)

        return schemas.InstitutionActorsShow.model_validate(institution_db)

    @staticmethod
    @db_session
    def delete_institution_actors(institution_actors_id: UUID):
        institution_actors_db = models.InstitutionActors.get_for_update(id=institution_actors_id)
        admin_db = institution_actors_db.admin
        institution_actors_db.delete()
        admin_db.delete()

    @staticmethod
    @db_session
    def create_location(location: schemas.LocationCreate) -> schemas.LocationShow:
        admin_db = models.Person.get(id=location.admin_id)
        institution_actors_db = models.InstitutionActors.get(id=location.institution_actors_id)
        new_location = models.Location(name=location.name, admin=admin_db, institution_actors=institution_actors_db)
        return schemas.LocationShow.model_validate(new_location)

    @staticmethod
    @db_session
    def delete_location(location_id):
        location_db = models.Location.get_for_update(id=location_id)
        admin_db = location_db.admin
        location_db.delete()
        admin_db.delete()
