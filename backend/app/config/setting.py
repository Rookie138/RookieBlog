import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from app.config.path_conf import ENV_DIR


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_DIR / f".env.{os.getenv('ENVIRONMENT', 'dev')}",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    EXPIRE_ON_COMMIT: bool = False
    DATABASE_ECHO: bool = True

    DATABASE_NAME: str = "blog"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "000000"
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306

    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    @property
    def DB_URI(self):
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def ASYNC_DB_URI(self):
        return (
            f"mysql+asyncmy://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


def get_setting() -> Settings:
    return Settings()


settings = get_setting()
