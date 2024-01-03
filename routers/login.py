from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(tags=['login'])


@router.get('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        users = authenticate_user(form_data.username, form_data.password)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Error: {e}')
