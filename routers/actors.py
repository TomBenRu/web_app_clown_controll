from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from commands.services import request_handler
from database import db_services, schemas
from oaut2_authentication.authentication import verify_access_token__actor

router = APIRouter(prefix='/actors', tags=['Clown-Call'])


class CreateTeamData(BaseModel):
    location_id: UUID
    user_ids: list[UUID]


@router.get('/all_actors')
def get_all_actors(token_data: schemas.TokenData = Depends(verify_access_token__actor)):
    actor = db_services.Actor.get(token_data.id)
    return db_services.Actor.get_all_actors_of_institution_actors(actor.institution_actors.id)


@router.get('/all_available_actors')
def get_all_available_actors(token_data: schemas.TokenData = Depends(verify_access_token__actor)):
    actor = db_services.Actor.get(token_data.id)
    return db_services.Actor.get_all_available_actors_of_institution_actors(actor.institution_actors.id)


@router.get('/locations')
def get_all_locations(token_data: schemas.TokenData = Depends(verify_access_token__actor)):
    actor = db_services.Actor.get(token_data.id)
    return db_services.Actor.get_all_locations_of_institution_actors(actor.institution_actors.id)


@router.get('/departments_of_location', dependencies=[Depends(verify_access_token__actor)])
def get_all_departments_of_location(location_id: UUID):
    return db_services.Actor.get_all_departments_of_location(location_id)


@router.get('/team_of_actors', dependencies=[Depends(verify_access_token__actor)])
def get_team_of_actors(team_of_actors_id: UUID):
    return db_services.Actor.get_team_of_actors(team_of_actors_id)


@router.post('/new-team', dependencies=[Depends(verify_access_token__actor)])
def create_new_team(new_team_data: schemas.TeamOfActorsCreate):
    return request_handler.create_team_of_actors(new_team_data)


@router.delete('/delete-team')
def delete_team(team_of_actor_id: str, token_data: schemas.TokenData = Depends(verify_access_token__actor)):
    return request_handler.delete_team_of_actors(UUID(team_of_actor_id))


@router.get('/session_messages', dependencies=[Depends(verify_access_token__actor)])
def get_session_messages(team_of_actors_id: UUID):
    return [schemas.SessionMessageShow.model_validate(sm)
            for sm in db_services.Actor.get_all_session_messages_of_team_of_actors(team_of_actors_id, False)]


@router.post('/set_all_messages_to_unsent', dependencies=[Depends(verify_access_token__actor)])
def set_all_messages_to_unsent(team_of_actors_id: UUID):
    print(f'in set_all_messages_to_unsent()..................................... {team_of_actors_id=}')
    db_services.Actor.set_all_messages_to_unsent(team_of_actors_id)

