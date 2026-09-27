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


    """
    #########################################################################
    ##################  Mysql数据库信息     ###################################
    #########################################################################
    """
    EXPIRE_ON_COMMIT: bool = False
    DATABASE_ECHO: bool = True

    DATABASE_NAME: str = "blog"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "<000000>"
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306

    """
    #########################################################################
    ##################   JWT配置信息      ####################################
    #########################################################################
    """
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    """
    #########################################################################
    ##################   Redis配置信息      ###################################
    #########################################################################
    """

    REDIS_USER: str = "root"
    REDIS_PASSWORD: str = "<PASSWORD>"
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB_NAME: str = "blog"

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

    @property
    def redis_db_url(self):
        redis_connect_url = f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_NAME}"
        return redis_connect_url

def get_setting() -> Settings:
    return Settings()


settings = get_setting()
