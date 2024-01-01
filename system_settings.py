from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    """Reads the variables of the most recent .env file in hierarchy. Variable names are not case sensitiv."""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # sqlite local
    provider: str
    db_clown_control: str


settings = Settings()
