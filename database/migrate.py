import sqlite3
import hashlib
import secrets
from config import Config
from database.models import SCHEMA, SEED


def migrate():
    with sqlite3.connect(Config.DB_PATH) as db:
        cursor = db.cursor()

        # ── asosiy schema (users, orders, etc.)
        db.executescript(SCHEMA)

        # ── seed data
        db.executescript(SEED)

        # ── NEWS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT,
                link_url TEXT,
                button_text TEXT,
                show_banner INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── DEPOSITS MIGRATION
        cursor.execute("PRAGMA table_info(deposits)")
        cols = [row[1] for row in cursor.fetchall()]

        if "receipt_uploaded_at" not in cols:
            try:
                cursor.execute("""
                    ALTER TABLE deposits 
                    ADD COLUMN receipt_uploaded_at TIMESTAMP
                """)
            except Exception:
                pass

        # ── ADMIN SEED (faqat 1 marta)
        pw = hashlib.sha256(Config.ADMIN_PASS.encode()).hexdigest()
        key = secrets.token_hex(16)
        rc = secrets.token_hex(4).upper()

        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (username, email, password, role, api_key, ref_code)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            Config.ADMIN_USER,
            Config.ADMIN_EMAIL,
            pw,
            "admin",
            key,
            rc
        ))

        db.commit()

    print(f"[DB] Migration done ✔️ {Config.DB_PATH}")


if __name__ == "__main__":
    migrate()