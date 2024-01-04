from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from database import db_services, schemas
from oaut2_authentication.authentication import oauth2_scheme

router = APIRouter(prefix='/admin', tags=['Adnim'])


@router.post('/actor')
async def create_actor(actor: schemas.ActorCreate, access_token: str = Depends(oauth2_scheme)):
    ...
