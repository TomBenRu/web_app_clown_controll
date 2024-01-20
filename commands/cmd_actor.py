from uuid import UUID

from commands.command_base_classes import Command
from database import schemas, db_services


class CreateTeamOfActors(Command):
    def __init__(self, team_of_actors: schemas.TeamOfActorsCreate):
        self.team_of_actors = team_of_actors
        self.created_team_of_actors: schemas.TeamOfActorsShow | None = None

    def execute(self):
        self.created_team_of_actors = db_services.Actor.create_team_of_actors(self.team_of_actors)

    def undo(self):
        db_services.Actor.delete_team_of_actors(self.created_team_of_actors.id)

    def redo(self):
        team_of_actors = schemas.TeamOfActorsCreate(id=self.created_team_of_actors.id,
                                                    location_id=self.team_of_actors.location_id,
                                                    actor_ids=self.team_of_actors.actor_ids)
        db_services.Actor.create_team_of_actors(team_of_actors)


class DeleteTeamOfActors(Command):
    def __init__(self, team_of_actors_id: UUID):
        self.team_of_actors_id = team_of_actors_id
        self.deleted_team_of_actors = db_services.Actor.get_team_of_actors(self.team_of_actors_id)

    def execute(self):
        self.deleted_team_of_actors = db_services.Actor.delete_team_of_actors(self.team_of_actors_id)

    def undo(self):
        new_team_of_actors = schemas.TeamOfActorsCreate(id=self.deleted_team_of_actors.id,
                                                        location_id=self.deleted_team_of_actors.location.id,
                                                        actor_ids=[a.id for a in self.deleted_team_of_actors.actors])
        db_services.Actor.create_team_of_actors(new_team_of_actors)

    def redo(self):
        db_services.Actor.delete_team_of_actors(self.team_of_actors_id)