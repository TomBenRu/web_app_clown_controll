from fastapi import APIRouter, Request, status
from starlette.responses import RedirectResponse

from database.enums import AuthorizationTypes
from oaut2_authentication import authentication

router = APIRouter(prefix='/connection_test', tags=['Connection Test'])


@router.get('/')
def test():
    return {'success': True}

