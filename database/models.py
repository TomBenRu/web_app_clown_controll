import datetime
from uuid import UUID

from pony.orm import Database, PrimaryKey, Required, Set, Optional, composite_key

db_clown_control = Database()


class Location(db_clown_control.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str, 50, unique=True)
    created_at = Required(datetime.date, default=lambda: datetime.date.today())
    last_modified = Required(datetime.datetime, default=datetime.datetime.now(datetime.timezone.utc))
    prep_delete = Optional(datetime.datetime)
    departments = Set('Department')
    teams_of_actors = Set('TeamOfActors')

    def before_update(self):
        self.last_modified = datetime.datetime.now(datetime.timezone.utc)


class Department(db_clown_control.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str, 50)
    descriptive_name = Required(str, 50)
    username = Required(str, 50, unique=True)
    password = Required(str, 50)
    created_at = Required(datetime.date, default=lambda: datetime.date.today())
    last_modified = Required(datetime.datetime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    prep_delete = Optional(datetime.datetime)
    location = Required(Location)

    composite_key(name, location)

    def before_update(self):
        self.last_modified = datetime.datetime.now(datetime.timezone.utc)


class Actor(db_clown_control.Entity):
    id = PrimaryKey(UUID, auto=True)
    f_name = Required(str, 50)
    l_name = Required(str, 50)
    artist_name = Required(str, 50)
    username = Required(str, 50, unique=True)
    password = Required(str, 50)
    created_at = Required(datetime.date, default=lambda: datetime.date.today())
    last_modified = Required(datetime.datetime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    prep_delete = Optional(datetime.datetime)
    team_of_actors = Optional('TeamOfActors')

    def before_update(self):
        self.last_modified = datetime.datetime.now(datetime.timezone.utc)


class TeamOfActors(db_clown_control.Entity):
    id = PrimaryKey(UUID, auto=True)
    actors = Set(Actor)
    location = Required(Location)
