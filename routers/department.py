import datetime
from functools import partial

from fastapi import APIRouter, Request, Header, status, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from database import db_services, schemas
from database.enums import AuthorizationTypes
from oaut2_authentication import authentication

templates = Jinja2Templates(directory='templates')

router = APIRouter(prefix='/department', tags=['Clown-Call'])


@router.get("/")
async def department_chat(request: Request, hx_request: str | None = Header(default=None)):
    try:
        authentication.get_current_user_cookie(request, 'clown-call-auth', AuthorizationTypes.department)
    except Exception as e:
        redirect_url = request.url_for('user_login')
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    if hx_request:
        return
    return templates.TemplateResponse('chat_clown_call.html.j2',
                                      context={'request': request, 'page_title': 'Clown-Call'})
