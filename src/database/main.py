from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from typing import Any, AsyncGenerator

from src.config import Config

asyncEngine = create_async_engine(
    url=Config.DATABASE_URL
)  # Their are also many kw like max_pool and so on for optimization

session = sessionmaker(bind=asyncEngine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[Any, AsyncSession]:
    async with session() as Session:
        yield Session
