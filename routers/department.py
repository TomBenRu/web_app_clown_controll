import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import db_services

templates = Jinja2Templates(directory='templates')

router = APIRouter(prefix='/department', tags=['Clown-Call'])


@router.get("/")
async def get(request: Request):
    # db_services.Actor.create()
    actors = db_services.Actor.get_all()
    print(f'{actors=}')
    print(f'{db_services.User.get(actors[0].id)=}')

    return templates.TemplateResponse('chat_clown_call.html.j2',
                                      context={'request': request,
                                               'user_name': datetime.datetime.now().strftime('%d.%m.%y-%H:%M:%S')})
