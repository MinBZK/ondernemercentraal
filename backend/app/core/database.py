from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import settings


def get_connection_string(use_async: bool = True) -> str:
    driver = "postgresql+asyncpg" if use_async else "postgresql+psycopg2"
    return (
        f"{driver}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


async_engine = create_async_engine(
    get_connection_string(),
    pool_size=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
