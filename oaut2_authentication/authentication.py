import datetime

from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from database import schemas, db_services
from database.emums import AuthorizationTypes
from system_settings import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                      detail='Could not validate credentials.',
                                      headers={'WWW-Authenticate': 'Bearer'})


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_psw(password: str):
    return pwd_context.hash(password)


def verify(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data['exp'] = expire
    return jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, role: AuthorizationTypes) -> schemas.TokenData:
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


def get_current_user_cookie(request: Request, token_key: str, role: AuthorizationTypes):
    token: str | None = request.cookies.get(token_key)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='you have to log in first')

    return verify_access_token(token, role)


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
        username: str, passwort: str) -> schemas.SuperUser | schemas.Admin | schemas.Department | schemas.Actor:
    if not (user := db_services.User.get_user_by_username(username)):
        raise credentials_exception
    if not verify(passwort, user.password):
        raise credentials_exception
    return user
