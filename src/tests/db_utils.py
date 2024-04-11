import uuid
from argparse import Namespace
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncIterator

import sqlalchemy as sa
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import make_url, _set_url_database
from sqlalchemy_utils.functions.orm import quote
from yarl import URL

from src.core import settings


def make_alembic_config(
        cmd_opts: Namespace,
        base_path: str | Path = settings.BASE_DIR,
) -> AlembicConfig:
    # Путь к файлу alembic.ini
    base_path = Path(base_path)
    if not Path(cmd_opts.config).is_absolute():
        cmd_opts.config = str(base_path.joinpath(cmd_opts.config).absolute())

    # Alembic config
    config = AlembicConfig(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,
    )

    # Путь к папке alembic
    alembic_location = config.get_main_option('script_location')
    if not Path(alembic_location).is_absolute():
        config.set_main_option(
            'script_location', str(base_path.joinpath(alembic_location).absolute())
        )
    if cmd_opts.pg_url:
        config.set_main_option(
            'sqlalchemy.url', cmd_opts.pg_url
        )
    return config


def alembic_config_from_url(pg_url: str | None = None) -> AlembicConfig:
    cmd_opts = Namespace(
        config='alembic.ini',
        name='alembic',
        pg_url=pg_url,
        raiseerr=True,
    )
    return make_alembic_config(cmd_opts=cmd_opts)


@asynccontextmanager
async def temp_database(db_url: URL, **kwargs) -> AsyncIterator[str]:
    """Контекстный менеджер для создания тестовой базы и ее удалении при завершении тестов"""
    temp_db_name = '.'.join([uuid.uuid4().hex, 'tests_base'])
    temp_db_url = str(db_url.with_path(temp_db_name))

    await create_test_db_async(url=temp_db_url, **kwargs)
    try:
        yield temp_db_url
    finally:
        await drop_temp_db_async(url=temp_db_url)


async def create_test_db_async(
        url: str,
        encoding: str = 'utf8',
        template: str | None = None,
) -> None:
    """Функция для создания тестовой базы"""
    url = make_url(url)
    database = url.database
    url = _set_url_database(url=url, database='postgres')
    engine = create_async_engine(url=url, isolation_level='AUTOCOMMIT')
    if not template:
        template = 'template1'

    async with engine.begin() as connection:
        stmt = f'CREATE DATABASE {quote(connection, database)} ENCODING {encoding} TEMPLATE {quote(connection, template)}'
        await connection.execute(sa.text(stmt))

    await engine.dispose()


async def drop_temp_db_async(url: str):
    """Функция для удаления тестовой базы"""
    url = make_url(url)
    database = url.database
    url = _set_url_database(url=url, database='postgres')
    engine = create_async_engine(url=url, isolation_level='AUTOCOMMIT')

    async with engine.begin() as connection:
        # Завершает сеанс, внутренний процесс которого имеет указанный идентификатор
        stmt = f"""SELECT pg_terminate_backend(pg_stat_activity.pid) 
        FROM pg_stat_activity 
        WHERE pg_stat_activity.datname = '{database}' AND pid <> pg_backend_pid();"""
        await connection.execute(sa.text(stmt))

        # Удаление базы
        stmt = f'DROP DATABASE {quote(connection, database)}'
        await connection.execute(sa.text(stmt))

    await engine.dispose()
