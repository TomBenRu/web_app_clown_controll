from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from database import db_services
from oaut2_authentication.authentication import verify_access_token__actor

router = APIRouter(prefix='/actors', tags=['Clown-Call'])


@router.get('/all_actors', dependencies=[Depends(verify_access_token__actor)])
def get_all_actors():
    return db_services.Actor.get_all_actors()
