from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker

from typing import AsyncGenerator, Any
from src.config import Config

async_engine = create_async_engine(
    url=Config.DATABASE_URL
)  # Their are also many kw like max_pool and so on for optimization

Session = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[Any, AsyncSession]:
    async with Session() as session:
        yield session
