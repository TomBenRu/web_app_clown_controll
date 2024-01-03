import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Actor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    f_name: str
    l_name: str
    artist_name: str
    username: str
    password: str
    created_at: datetime.date
    last_modified: datetime.datetime
    # prep_delete: Optional[datetime.datetime]


class TokenData(BaseModel):
    id: UUID | str | None = None
    authorizations: list[str]
