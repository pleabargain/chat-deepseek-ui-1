from utils import logger
import redis
import time
from const import DB_PARAMS, REDIS_URL

try:
    import psycopg2
except ImportError as e:
    logger.error("Failed to import psycopg2. Please install it using: pip install psycopg2", exc_info=True)
    raise

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Redis Connection with retries
def get_redis_connection():
    for attempt in range(MAX_RETRIES):
        try:
            return redis.Redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to connect to Redis after {MAX_RETRIES} attempts", exc_info=True)
                raise
            logger.warning(f"Redis connection attempt {attempt + 1} failed, retrying...")
            time.sleep(RETRY_DELAY)

# Initialize Redis client
try:
    redis_client = get_redis_connection()
except Exception as e:
    logger.error("Failed to initialize Redis client", exc_info=True)
    raise

def get_db_connection():
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            # Test the connection
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return conn
        except Exception as e:
            last_error = e
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to connect to PostgreSQL database after {MAX_RETRIES} attempts", exc_info=True)
                logger.error(f"Database parameters: host={DB_PARAMS['host']}, port={DB_PARAMS['port']}, dbname={DB_PARAMS['dbname']}, user={DB_PARAMS['user']}")
                raise
            logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
            time.sleep(RETRY_DELAY)

# Save session details
def save_session(name, model):
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (name, model) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id;",
                (name, model)
            )
            session_id = cur.fetchone()
            conn.commit()
            return session_id
    except Exception as e:
        logger.error(f"Failed to save session. name={name}, model={model}", exc_info=True)
        raise

# Fetch session by name
def get_session(name):
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, model FROM sessions WHERE name = %s;", (name,))
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Failed to get session. name={name}", exc_info=True)
        raise

# Fetch all session names
def get_all_sessions():
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT name FROM sessions;")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.error("Failed to get all sessions", exc_info=True)
        raise

# Save message
def save_message(session_id, role, content):
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s);",
                        (session_id, role, content))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to save message. session_id={session_id}, role={role}", exc_info=True)
        raise

# Fetch chat history from database
def get_chat_history(session_id):
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at ASC;", (session_id,))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Failed to get chat history. session_id={session_id}", exc_info=True)
        raise
