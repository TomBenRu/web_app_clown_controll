from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import db_services, schemas

router = APIRouter(prefix='/superuser', tags=['Superuser'])


@router.put('/')
def create(user: schemas.SuperUserCreate):
    return db_services.create_superuser(user)
