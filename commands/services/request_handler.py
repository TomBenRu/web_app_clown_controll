from commands import cmd_admin, cmd_super_user
from database import schemas, password_utils


def create_admin(admin: schemas.AdminCreate):
    hashed_password = password_utils.hash_psw(admin.password)
    admin.password = hashed_password
    create_cmd = cmd_super_user.CreateAdmin(admin)
    create_cmd.execute()
    return create_cmd.created_admin
