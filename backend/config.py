import psycopg2
import redis
from const import DB_PARAMS, REDIS_URL


def get_db_connection():
    """Returns a new database connection."""
    return psycopg2.connect(**DB_PARAMS)


# Redis Connection
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
