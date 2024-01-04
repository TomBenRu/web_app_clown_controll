from commands.command_base_classes import Command
from database import schemas, password_utils, db_services


class CreateAdmin(Command):
    def __init__(self, admin: schemas.AdminCreate):
        self.admin = admin
        self.admin.password = password_utils.hash_psw(self.admin.password)
        self.created_admin: schemas.Admin | None = None

    def execute(self):
        self.created_admin = db_services.SuperUser.create_admin(self.admin)

    def undo(self):
        db_services.SuperUser.delete_admin(self.created_admin.id)

    def redo(self):
        db_services.SuperUser.create_admin(self.admin, self.created_admin.id)
