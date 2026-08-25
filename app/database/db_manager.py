import sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.core.config import DATABASE_PATH
from app.core.exceptions import DatabaseError
from app.core.logger import logger


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        schema_path = Path(__file__).parent / "schema.sql"
        try:
            with self.get_connection() as conn:
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization error: {e}")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database transaction error: {e}")
        finally:
            conn.close()
