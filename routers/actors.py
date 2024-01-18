from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import db_services, schemas
from oaut2_authentication.authentication import verify_access_token__actor

router = APIRouter(prefix='/actors', tags=['Clown-Call'])


class CreateTeamData(BaseModel):
    location_id: UUID
    user_ids: list[UUID]


@router.get('/all_actors', dependencies=[Depends(verify_access_token__actor)])
def get_all_actors():
    return db_services.Actor.get_all_actors()

@router.get('/locations', dependencies=[Depends(verify_access_token__actor)])
def get_all_locations():
    return db_services.Actor.get_all_locations()

@router.post('/new-team', dependencies=[Depends(verify_access_token__actor)])
def create_new_team(data: CreateTeamData):  # TODO: Relationship between InstitutionActors and Locations to implement
    print(f'{data=}')
    return

    return db_services.Actor.create_new_team(new_team)
