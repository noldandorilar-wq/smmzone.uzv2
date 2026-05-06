import sqlite3
from config import Config
from database.models import SCHEMA, SEED


def init_db():
    """
    Database ni yaratadi va schema + seed data yuklaydi
    """
    with sqlite3.connect(Config.DB_PATH) as db:
        cursor = db.cursor()

        # schema yaratish
        db.executescript(SCHEMA)

        # seed data (boshlang‘ich ma’lumotlar)
        db.executescript(SEED)

        # news table (agar SCHEMA ichida bo‘lmasa)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.commit()