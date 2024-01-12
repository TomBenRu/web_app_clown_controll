import datetime

from fastapi import APIRouter, Request, Header
from fastapi.templating import Jinja2Templates

from database import db_services

templates = Jinja2Templates(directory='templates')

router = APIRouter(prefix='/department', tags=['Clown-Call'])


@router.get("/")
async def chat(request: Request, hx_request: str | None = Header(default=None)):
    if hx_request:
        return
    response = templates.TemplateResponse('chat_clown_call.html.j2',
                                          context={'request': request, 'page_title': 'Clown-Call'})
    response.set_cookie(key='ws-cookie', value='department-token')
    return response
