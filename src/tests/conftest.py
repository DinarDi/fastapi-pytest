from asyncio import Task

import pytest
from httpx import AsyncClient
from yarl import URL
from alembic.command import upgrade

from src.core import settings
from .db_utils import temp_database, alembic_config_from_url
from src.database import db_manager, Base


MIGRATION_TASK: Task | None = None


@pytest.fixture()
def app():
    # Создание тестового приложения FastAPI
    from main import app
    yield app


@pytest.fixture()
async def client(session, app):
    # Создание тестового клиента
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture(scope='session', autouse=True)
def anyio_backend():
    return 'asyncio', {'use_uvloop': True}


@pytest.fixture(scope='session')
def pg_url():
    """Предоставляет базовый URL для создания временной базы"""
    return URL(settings.DB_URL)


@pytest.fixture(scope='session')
async def pg_template_with_migrations(pg_url):
    """Создает временную базу и применяет миграции"""
    async with temp_database(pg_url) as temp_url:
        alembic_config = alembic_config_from_url(temp_url)
        settings.DB_URL = temp_url
        upgrade(alembic_config, 'head')
        await MIGRATION_TASK
        yield temp_url


@pytest.fixture(scope='session')
async def sessionmanager_for_tests(pg_template_with_migrations):
    db_manager.init_connection(db_url=pg_template_with_migrations)
    yield db_manager
    await db_manager.close_connection()


@pytest.fixture()
async def session(sessionmanager_for_tests):
    async with db_manager.session() as session:
        yield session

    # Очистка таблиц после каждого теста
    async with db_manager.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            await connection.execute(table.delete())
        await connection.commit()
