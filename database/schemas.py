import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class Location(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime.date
    last_modified: datetime.datetime
    prep_delete: Optional[datetime.datetime]
    departments: list['Department']
    teams_of_actors: list['TeamOfActors']

    @field_validator('departments', 'teams_of_actors')
    def set_to_list(cls, values):  # sourcery skip: identity-comprehension
        return [v for v in values]


class Department(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    password: str
    name: str
    descriptive_name: str
    location: Location


class ActorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str
    f_name: str
    l_name: str
    artist_name: str


class Actor(ActorCreate):

    id: UUID
    team_of_actors: Optional['TeamOfActors']


class TeamOfActorsCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location: Location


class TeamOfActors(TeamOfActorsCreate):

    id: UUID
    actors: list[Actor]

    @field_validator('actors')
    def set_to_list(cls, values):  # sourcery skip: identity-comprehension
        return [v for v in values]


class AdminCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str
    f_name: str
    l_name: str


class Admin(AdminCreate):

    id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: UUID | str | None = None
    authorizations: list[str]
