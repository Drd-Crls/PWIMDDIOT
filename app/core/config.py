from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_key_prefix: str = "iotk_"
    api_key_bytes: int = 32

    class Config:
        env_file = ".env"


settings = Settings()
