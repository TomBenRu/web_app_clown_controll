from uuid import UUID

import commands.cmd_super_user
from commands import cmd_admin, cmd_super_user, cmd_actor
from database import schemas, password_utils, db_services


def create_person(person: schemas.PersonCreate) -> schemas.PersonShow:
    hashed_password = password_utils.hash_psw(person.password)
    person.password = hashed_password
    create_cmd_admin = cmd_super_user.CreateAdmin(person)
    create_cmd_admin.execute()
    return create_cmd_admin.created_admin


def create_institution_actors(admin: schemas.PersonCreate, institution_actors: schemas.InstitutionActorsCreate):
    institution_actors.admin_id = create_person(admin).id
    create_cmd_institution_actors = cmd_super_user.CreateInstitutionActors(institution_actors)
    create_cmd_institution_actors.execute()

    return create_cmd_institution_actors.created_institution_actors


def create_actor(actor: schemas.ActorCreate):
    hashed_password = password_utils.hash_psw(actor.password)
    actor.password = hashed_password
    create_cmd = cmd_admin.CreateActor(actor)
    create_cmd.execute()
    return create_cmd.created_actor


def create_location(admin: schemas.PersonCreate, location: schemas.LocationCreate):
    location.admin_id = create_person(admin).id
    create_cmd = commands.cmd_super_user.CreateLocation(location)
    create_cmd.execute()
    return create_cmd.created_location


def create_department(department: schemas.DepartmentCreate):
    hashed_psw = password_utils.hash_psw(department.password)
    department.password = hashed_psw
    create_cmd = cmd_admin.CreateDepartment(department)
    create_cmd.execute()
    return create_cmd.created_department


def create_team_of_actors(team_of_actors: schemas.TeamOfActorsCreate):
    create_cmd = cmd_actor.CreateTeamOfActors(team_of_actors)
    create_cmd.execute()
    return create_cmd.created_team_of_actors


def delete_team_of_actors(team_of_actors_id: UUID):
    delete_cmd = cmd_actor.DeleteTeamOfActors(team_of_actors_id)
    delete_cmd.execute()
    return delete_cmd.deleted_team_of_actors