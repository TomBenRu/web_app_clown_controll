from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from commands.services import request_handler
from database import db_services, schemas
from oaut2_authentication.authentication import verify_access_token__admin

router = APIRouter(prefix='/admin', tags=['Admin'])

# todo: Unterscheidung admin_loc und admin_actors


@router.post('/actor', dependencies=[Depends(verify_access_token__admin)])
def create_actor(actor: schemas.ActorCreate):
    return request_handler.create_actor(actor)


@router.post('/department', dependencies=[Depends(verify_access_token__admin)])
def create_department(department: schemas.DepartmentCreate):
    return request_handler.create_department(department)


@router.post('/location', dependencies=[Depends(verify_access_token__admin)])
def create_location(location: schemas.LocationCreate):
    return request_handler.create_location(location)


