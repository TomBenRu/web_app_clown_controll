from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Reads the variables of the most recent .env file in hierarchy. Variable names are not case sensitiv."""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # sqlite local
    provider: str
    db_clown_control: str

try:
    settings = Settings()
except Exception as e:
    print(f'Trying to get Settings from Environment:\n{e}\nNow I check the .env-file:')
    settings = Settings(_env_file='.env')
