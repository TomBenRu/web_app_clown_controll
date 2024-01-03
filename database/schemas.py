import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    password: str


class Person(User):
    f_name: str
    l_name: str


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


class Department(User):
    model_config = ConfigDict(from_attributes=True)

    name: str
    descriptive_name: str
    location: Location


class Actor(Person):
    model_config = ConfigDict(from_attributes=True)

    artist_name: str
    team_of_actors: Optional['TeamOfActors']


class TeamOfActors(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actors: list[Actor]
    location: Location

    @field_validator('actors')
    def set_to_list(cls, values):  # sourcery skip: identity-comprehension
        return [v for v in values]


class Admin(Person):
    ...


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: UUID | str | None = None
    authorizations: list[str]
