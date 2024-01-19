from fastapi import APIRouter, Request, Depends

from commands.services import request_handler
from database import db_services, schemas
from oaut2_authentication.authentication import (verify_access_token__admin_of_location,
                                                 verify_access_token__admin_of_institution_actors)

router = APIRouter(prefix='/admin', tags=['Admin'])

# todo: Unterscheidung admin_loc und admin_actors


@router.post('/actor', dependencies=[Depends(verify_access_token__admin_of_institution_actors)])
def create_actor(user: schemas.ActorCreate):
    return request_handler.create_actor(user)


@router.post('/department', dependencies=[Depends(verify_access_token__admin_of_location)])
def create_department(department: schemas.DepartmentCreate):
    return request_handler.create_department(department)


@router.post('/location', dependencies=[Depends(verify_access_token__admin_of_institution_actors)])
def create_location(user: schemas.PersonCreate, location: schemas.LocationCreate):
    return request_handler.create_location(user, location)


