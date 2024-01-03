import datetime

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from database import schemas
from database.emums import AuthorizationTypes
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


def get_authorization_types(user: schemas.PersonShow) -> list[AuthorizationTypes]:
    auth_types = []
    if user.team_of_actor:
        auth_types.append(AuthorizationTypes.actor)
    if user.project_of_admin:
        auth_types.append(AuthorizationTypes.admin)
    if user.teams_of_dispatcher:
        auth_types.append(AuthorizationTypes.dispatcher)
    return auth_types


def authenticate_user(username: str, passwort: str) -> schemas.PersonShow | str:
    if username == SUPERVISOR_USERNAME:
        if utils.verify(passwort, SUPERVISOR_PASSWORD):
            return 'supervisor'
    if not (user := services.Person.find_user_by_email(email=username)):
        raise credentials_exception
    if not utils.verify(passwort, user.password):
        raise credentials_exception
    return user


def verify_actor_username(username: str) -> schemas.PersonShow | None:
    if user := services.Person.find_user_by_email(username):
        if user.team_of_actor:
            return user
    return None

