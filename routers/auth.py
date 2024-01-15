from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from database import schemas
from oaut2_authentication.authentication import authenticate_user, get_authorization_types, create_access_token, \
    get_current_user_cookie

router = APIRouter(tags=['login'])

templates = Jinja2Templates(directory='templates')


@router.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Error: {e}')

    auth_types = get_authorization_types(user)
    access_token = create_access_token(data={'user_id': str(user.id),
                                             'roles': [a_t.value for a_t in auth_types]})

    return schemas.Token(access_token=access_token, token_type='bearer')


@router.get('/login')
async def user_login(request: Request):
    return templates.TemplateResponse('user_login.html.j2', context={'request': request})


@router.post('/authorize')
async def authorize(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        return templates.TemplateResponse('responses/user_login_rejected.html.j2', context={'request': request})
    auth_types = get_authorization_types(user)
    if not auth_types:
        return templates.TemplateResponse('responses/user_login_rejected.html.j2', context={'request': request})
    access_token = create_access_token(data={'user_id': str(user.id), 'roles': [a_t.value for a_t in auth_types]})
    response = templates.TemplateResponse('responses/user_login_accepted.html.j2', context={'request': request})
    response.set_cookie('clown-call-auth', value=access_token, httponly=True)
    return response


@router.get('/login_success')
def login_success(request: Request, token_data: schemas.TokenData = Depends(get_current_user_cookie)):
    print(f'{token_data.authorizations=}')
    if 'department' in token_data.authorizations:
        return templates.TemplateResponse('responses/redirect_to_department_chat.html.j2', context={'request': request})
    return '<p>Es gibt noch keinen Zugang für dein Anliegen</p>'



