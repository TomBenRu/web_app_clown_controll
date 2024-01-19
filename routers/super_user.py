from functools import partial

from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from commands.services import request_handler
from database import db_services, schemas, password_utils, enums
from oaut2_authentication.authentication import verify_access_token__superuser

router = APIRouter(prefix='/superuser', tags=['Superuser'])


@router.post('/')
def create(user: schemas.SuperUserCreate):
    hashed_psw = password_utils.hash_psw(user.password)
    user.password = hashed_psw
    try:
        return db_services.create_superuser(user)
    except Exception as e:
        return {'Kein Erfolg': f'Fehler: {e}'}


@router.post('/institution-actors', dependencies=[Depends(verify_access_token__superuser)])
def create_institution_actors(user: schemas.PersonCreate, institution_actors: schemas.InstitutionActorsCreate):
    return request_handler.create_institution_actors(user, institution_actors)
