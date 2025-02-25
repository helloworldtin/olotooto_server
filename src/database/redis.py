from redis.asyncio import Redis

from src.config import Config
from src.exceptions.exceptions import InterServerException

redis = Redis.from_url(Config.REDIS_URL)


async def put_data_in_redis(key: str, data: str) -> bool:
    """only save string data for this project"""
    try:
        await redis.set(key=key, value=data)
    except Exception as e:
        print(f"Error While saving data in redis {e}")
        raise InterServerException()


async def get_data_from_redis(key: str) -> str | None:
    try:
        data: str | None = await redis.get(key)
        return data
    except Exception as e:
        print(f"Error While getting data from redis {e}")
        raise InterServerException()
