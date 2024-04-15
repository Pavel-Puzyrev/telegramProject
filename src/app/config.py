import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from app import SRC_DIR


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=SRC_DIR / '.env',
        env_file_encoding='utf-8',
        env_prefix='PPI_'
    )

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    pg_driver: str | None = None
    # pg_driver: str = 'psycopg2'

    log_level: str = logging.INFO  # Enum
    # В файле env.example к списку логгеров также добавлен sqlalchemy.engine.
    # То есть идея в том, что по умолчанию логи алхимии не пишутся, но в локальном окружении
    # можно по необходимости включить их.
    loggers: str = 'uvicorn, uvicorn.access'
    debug: bool = False

    def build_db_url(self, driver: str | None = None) -> PostgresDsn:
        scheme = 'postgresql'
        if driver is not None:
            scheme += f'+{driver}'

        url = PostgresDsn.build(
            scheme=scheme,
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            path=self.db_name,
        )
        return str(url)

    @computed_field
    def sqlalchemy_db_url(self) -> PostgresDsn:
        return self.build_db_url(self.pg_driver)

    @computed_field
    def site_loggers_list(self) -> list[str]:
        return [subs.strip() for subs in self.loggers.split(',')]


settings = AppSettings()
