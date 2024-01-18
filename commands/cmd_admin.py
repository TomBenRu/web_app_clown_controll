from commands.command_base_classes import Command
from database import schemas, db_services


class CreateActor(Command):
    def __init__(self, actor: schemas.ActorCreate):
        self.actor = actor
        self.created_actor: schemas.Actor | None = None

    def execute(self):
        self.created_actor = db_services.Admin.create_account(self.actor)

    def undo(self):
        db_services.Admin.delete_account(self.created_actor)

    def redo(self):
        db_services.Admin.create_account(self.actor, self.created_actor.id)


class CreateDepartment(Command):
    def __init__(self, department: schemas.DepartmentCreate):
        self.department = department
        self.created_department: schemas.Department | None = None

    def execute(self):
        self.created_department = db_services.Admin.create_department(self.department)

    def undo(self):
        db_services.Admin.delete_department(self.created_department.id)

    def redo(self):
        db_services.Admin.create_department(self.department, self.created_department.id)
