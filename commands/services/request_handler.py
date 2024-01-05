from commands import cmd_admin, cmd_super_user
from database import schemas, password_utils, db_services


def create_admin(admin: schemas.AdminCreate):
    hashed_password = password_utils.hash_psw(admin.password)
    admin.password = hashed_password
    create_cmd = cmd_super_user.CreateAdmin(admin)
    create_cmd.execute()
    return create_cmd.created_admin


def create_actor(actor: schemas.ActorCreate):
    hashed_password = password_utils.hash_psw(actor.password)
    actor.password = hashed_password
    create_cmd = cmd_admin.CreateActor(actor)
    create_cmd.execute()
    return create_cmd.created_actor


def create_location(location: schemas.LocationCreate):
    create_cmd = cmd_admin.CreateLocation(location)
    create_cmd.execute()
    return create_cmd.created_location


def create_department(department: schemas.DepartmentCreate):
    hashed_psw = password_utils.hash_psw(department.password)
    department.password = hashed_psw
    create_cmd = cmd_admin.CreateDepartment(department)
    create_cmd.execute()
    return create_cmd.created_department
