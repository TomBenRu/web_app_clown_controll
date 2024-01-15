from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from starlette.datastructures import URL
from starlette.responses import RedirectResponse

from database import db_services
from database.enums import AuthorizationTypes
from oaut2_authentication import authentication

router = APIRouter(tags=['Index'])


@router.get('/')
def index(request: Request):
    try:
        authentication.get_current_user_cookie(request, 'wa-clown-control', AuthorizationTypes.department)
    except Exception as e:
        redirect_url = request.url_for('user_login')
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    return {'home': 'index'}

