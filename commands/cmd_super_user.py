from commands.command_base_classes import Command
from database import schemas, password_utils, db_services


class CreateAdmin(Command):
    def __init__(self, admin: schemas.PersonCreate):
        self.admin = admin
        self.created_admin: schemas.PersonShow | None = None

    def execute(self):
        self.created_admin = db_services.SuperUser.create_person(self.admin)

    def undo(self):
        db_services.SuperUser.delete_person(self.created_admin.id)

    def redo(self):
        admin_to_create = schemas.PersonCreate(id=self.created_admin.id, **self.admin.dict())
        db_services.SuperUser.create_person(admin_to_create)


class CreateInstitutionActors(Command):
    def __init__(self, institution_actors: schemas.InstitutionActorsCreate):
        self.institution_actors = institution_actors
        self.created_institution_actors: schemas.InstitutionActors | None = None

    def execute(self):
        self.created_institution_actors = db_services.SuperUser.create_institution_actors(self.institution_actors)

    def undo(self):
        db_services.SuperUser.delete_institution_actors(self.created_institution_actors.id)

    def redo(self):
        raise NotImplementedError


class CreateLocation(Command):
    def __init__(self, location: schemas.LocationCreate):
        self.location = location
        self.created_location: schemas.Location | None = None

    def execute(self):
        self.created_location = db_services.SuperUser.create_location(self.location)

    def undo(self):
        db_services.SuperUser.delete_location(self.created_location.id)

    def redo(self):
        raise NotImplementedError
