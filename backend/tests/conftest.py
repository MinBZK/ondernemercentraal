# from tests.fixtures.appointment import appointment  # noqa: F401
# from tests.fixtures.database import connection, session  # noqa: F401


from typing import AsyncGenerator

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, AsyncTransaction

import app.core.models as models
from app.core.database import async_engine
from app.core.settings import settings
from tests.fixtures import *  # noqa


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Inspired by:
    - https://gist.github.com/e-kondr01/969ae24f2e2f31bd52a81fa5a1fe0f96
    - https://fastapi.tiangolo.com/async/?h=anyio#write-your-own-async-code
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def connection(anyio_backend) -> AsyncGenerator[AsyncConnection, None]:
    async with async_engine.connect() as connection:
        yield connection


def pytest_sessionstart():
    settings.KEYCLOAK_URI = "dummy"
    settings.KEYCLOAK_API_CLIENT = "dummy"
    settings.KEYCLOAK_API_SECRET = "dummy"
    settings.KEYCLOAK_API_URI = "dummy"
    settings.LOG_LEVEL = "DEBUG"
    settings.DISABLE_AUTH = "0"


@pytest.fixture(scope="session")
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    async with connection.begin() as transaction:
        yield transaction


@pytest.fixture(scope="session")
async def session(connection: AsyncConnection, transaction: AsyncTransaction) -> AsyncGenerator[AsyncSession, None]:
    """
    This fancy session allows easy roll back of any changes made during testing, even if session.commit() is
    called anywhere. This keeps the integrity of your local DB. It also ensures an empty DB to start.
    """
    # If expire_on_commit =True, SQLAlchemy object fixtures would expire when a commit is called in the application.
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    await clear_database(async_session)
    yield async_session
    await transaction.rollback()


async def clear_database(async_session: AsyncSession):
    await async_session.execute(delete(models.Client))
    await async_session.execute(delete(models.AppointmentType))
    await async_session.execute(delete(models.Appointment))
