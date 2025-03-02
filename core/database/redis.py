from redis.asyncio import Redis

from src.config import Config
from core.exceptions.exceptions import InterServerException

redis = Redis.from_url(Config.REDIS_URL)


async def put_data_in_redis(key: str, data: str, expire_in_second: int = 120) -> bool:
    """only save string data for this project"""
    try:
        await redis.set(
            name=key,
            value=data,
            ex=expire_in_second,
        )
    except Exception as e:
        print(f"Error While saving data in redis {e}")
        raise InterServerException()


async def get_data_from_redis(key: str) -> str | None:
    try:
        data: bytes | None = await redis.get(key)
        return data.decode()
    except Exception as e:
        print(f"Error While getting data from redis {e}")
        raise InterServerException()


async def delete_data_from_redis(key: str) -> None:
    try:
        await redis.delete(key)
    except Exception as e:
        print(f"Error While deleting data from redis {e}")
