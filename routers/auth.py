from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from database import schemas
from oaut2_authentication.authentication import authenticate_user, get_authorization_types, create_access_token

router = APIRouter(tags=['login'])


@router.get('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Error: {e}')

    auth_types = get_authorization_types(user)
    access_token = create_access_token(data={'user_id': str(user.id),
                                             'roles': [a_t.value for a_t in auth_types]})

    return schemas.Token(access_token=access_token, token_type='bearer')
