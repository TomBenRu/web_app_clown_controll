from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import db_services


router = APIRouter(prefix='/department', tags=['Clown-Call'])

