import sqlite3
from config import Config
from database.models import SCHEMA, SEED


def init_db():
    """
    Database ni yaratadi va schema + seed data yuklaydi
    """
    with sqlite3.connect(Config.DB_PATH) as db:
        db.executescript(SCHEMA)
        db.executescript(SEED)
        db.commit()


from utils.security import hash_pw, gen_key, gen_ref
from config import Config


def init_db():
    with sqlite3.connect(Config.DB_PATH) as db:
        db.executescript(SCHEMA)
        db.executescript(SEED)

        # Admin yaratish
        existing = db.execute(
            "SELECT id FROM users WHERE role='admin'"
        ).fetchone()

        if not existing:
            db.execute(
                "INSERT INTO users (username, email, password, role, api_key, ref_code, is_active) "
                "VALUES (?, ?, ?, 'admin', ?, ?, 1)",
                (Config.ADMIN_USER, Config.ADMIN_EMAIL,
                 hash_pw(Config.ADMIN_PASS), gen_key(), gen_ref())
            )
            db.commit()