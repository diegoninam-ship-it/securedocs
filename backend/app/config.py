from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url_pooled: str
    database_url_unpooled: str
    jwt_secret: str
    jwt_expire_minutes: int = 30
    demo_mode: bool = False
    tz_app: str = "America/Lima"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()