import datetime
from functools import partial

import requests
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from database import schemas, db_services
from database.enums import AuthorizationTypes
from database.password_utils import verify
from system_settings import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
AUTH_SERVER_URL = 'https://hcc-plan-api.onrender.com'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                      detail='Could not validate credentials.',
                                      headers={'WWW-Authenticate': 'Bearer'})


def create_access_token(data: dict) -> str:
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data['exp'] = expire
    return jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(role: AuthorizationTypes | None, token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    print(f'Verifying access token with role {role}')
    print(f'Token: {token}')
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        if not (u_id := payload.get('user_id')):
            raise credentials_exception
        if role and role.value not in payload['roles']:
            raise credentials_exception
        token_data = schemas.TokenData(id=u_id, authorizations=payload['roles'])
    except JWTError as e:
        raise credentials_exception from e
    return token_data


verify_access_token__superuser = partial(verify_access_token, role=AuthorizationTypes.superuser)
verify_access_token__admin_of_location = partial(verify_access_token, role=AuthorizationTypes.admin_of_location)
verify_access_token__admin_of_institution_actors = partial(verify_access_token,
                                                           role=AuthorizationTypes.admin_of_institution_actors)
verify_access_token__actor = partial(verify_access_token, role=AuthorizationTypes.actor)


def get_current_user_cookie(request: Request, token_key: str = 'clown-call-auth',
                            role: AuthorizationTypes = None) -> schemas.TokenData:
    if token := request.cookies.get(token_key):
        return verify_access_token(role, token)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you have to log in first')


def get_authorization_types(
        user: schemas.SuperUser | schemas.PersonShow | schemas.Department | schemas.ActorShow) -> list[AuthorizationTypes]:
    auth_types = []
    if isinstance(user, schemas.SuperUser):
        auth_types.append(AuthorizationTypes.superuser)
    if isinstance(user, schemas.Person):
        if user.location_of_admin:
            auth_types.append(AuthorizationTypes.admin_of_location)
        if user.institution_actors_of_admin:
            auth_types.append(AuthorizationTypes.admin_of_institution_actors)
    if isinstance(user, schemas.Department):
        auth_types.append(AuthorizationTypes.department)
    if isinstance(user, schemas.Actor):
        auth_types.append(AuthorizationTypes.actor)
    return auth_types


def authenticate_user(
        username: str, password: str) -> schemas.SuperUser | schemas.Person | schemas.Department | schemas.Actor:
    if not (user := db_services.User.get_user_by_username(username)):
        try:
            response = requests.post(f'{AUTH_SERVER_URL}/user-login-from-clown-control',
                                     data={'username': username, 'password': password}, timeout=5)
            print(f'Authentication Actor: {response.json()}', flush=True)
        except Exception as e:
            raise credentials_exception from e
        raise credentials_exception
    if not verify(password, user.password):
        raise credentials_exception
    return user
