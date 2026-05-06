import sqlite3, hashlib, secrets
from config import Config
from database.models import SCHEMA, SEED

def init_db():
    with sqlite3.connect(Config.DB_PATH) as db:
        db.executescript(SCHEMA)
        db.executescript(SEED)

        # ── NEWS / REKLAMA jadvali ────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                title         TEXT NOT NULL,
                description   TEXT NOT NULL,
                image_url     TEXT,
                link_url      TEXT,
                button_text   TEXT,
                show_banner   INTEGER DEFAULT 1,
                is_active     INTEGER DEFAULT 1,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── DEPOSITS jadvaliga chek ustunlarini qo'shish ──────
        cols = [r[1] for r in db.execute("PRAGMA table_info(deposits)").fetchall()]
        if "receipt_uploaded_at" not in cols:
            try:
                db.execute("ALTER TABLE deposits ADD COLUMN receipt_uploaded_at TIMESTAMP")
            except Exception:
                pass

        # Admin user
        pw  = hashlib.sha256(Config.ADMIN_PASS.encode()).hexdigest()
        key = secrets.token_hex(16)
        rc  = secrets.token_hex(4).upper()
        db.execute(
            "INSERT OR IGNORE INTO users (username,email,password,role,api_key,ref_code) VALUES (?,?,?,?,?,?)",
            (Config.ADMIN_USER, Config.ADMIN_EMAIL, pw, "admin", key, rc)
        )
        db.commit()
    print(f"[DB] Tayyor: {Config.DB_PATH}")

if __name__ == "__main__":
    init_db()