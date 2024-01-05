import datetime
from functools import partial

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from database import schemas, db_services
from database.enums import AuthorizationTypes
from database.password_utils import verify
from system_settings import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                      detail='Could not validate credentials.',
                                      headers={'WWW-Authenticate': 'Bearer'})


def create_access_token(data: dict) -> str:
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data['exp'] = expire
    return jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(role: AuthorizationTypes, token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        if not (u_id := payload.get('user_id')):
            raise credentials_exception
        if role.value not in payload['roles']:
            raise credentials_exception
        token_data = schemas.TokenData(id=u_id, authorizations=payload['roles'])
    except JWTError as e:
        raise credentials_exception from e
    return token_data


verify_access_token__superuser = partial(verify_access_token, role=AuthorizationTypes.superuser)
verify_access_token__admin = partial(verify_access_token, role=AuthorizationTypes.admin)


def get_current_user_cookie(request: Request, token_key: str, role: AuthorizationTypes):
    if token := request.cookies.get(token_key):
        return verify_access_token(token, role)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you have to log in first')


def get_authorization_types(
        user: schemas.SuperUser | schemas.Admin | schemas.Department | schemas.Actor) -> list[AuthorizationTypes]:
    auth_types = []
    if isinstance(user, schemas.SuperUser):
        auth_types.append(AuthorizationTypes.superuser)
    if isinstance(user, schemas.Admin):
        auth_types.append(AuthorizationTypes.admin)
    if isinstance(user, schemas.Department):
        auth_types.append(AuthorizationTypes.department)
    if isinstance(user, schemas.Actor):
        auth_types.append(AuthorizationTypes.actor)
    return auth_types


def authenticate_user(
        username: str, password: str) -> schemas.SuperUser | schemas.Admin | schemas.Department | schemas.Actor:
    if not (user := db_services.User.get_user_by_username(username)):
        raise credentials_exception
    if not verify(password, user.password):
        raise credentials_exception
    return user
