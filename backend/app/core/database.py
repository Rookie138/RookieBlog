from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker

from app.config.setting import settings

def create_engine_and_session(db_url: str = settings.ASYNC_DB_URI) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:

    async_engine = create_async_engine(url=db_url,
                                       echo=settings.DATABASE_ECHO)

    async_session_local = async_sessionmaker(bind=async_engine,
                                             expire_on_commit=settings.EXPIRE_ON_COMMIT)

    return async_engine, async_session_local


async_engine, async_session_local = create_engine_and_session()