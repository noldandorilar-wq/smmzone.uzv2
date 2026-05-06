"""
config.py — Environment Variables'dan o'qiydi
Lokal'da: .env fayl yoki to'g'ridan default qiymatlar
Render'da: Environment Variables sozlamalaridan
"""
import os


def env(key, default=""):
    """Environment variable'ni olish, agar yo'q bo'lsa default"""
    return os.environ.get(key, default)


class Config:
    # ── Asosiy ──
    SECRET_KEY = env("SECRET_KEY", "change-me-to-random-string-in-production")
    SITE_NAME  = env("SITE_NAME", "SMMZONE")
    PORT       = int(env("PORT", "8000"))
    DB_PATH    = env("DB_PATH", "smm_panel.db")

    # ── Admin ──
    ADMIN_USER  = env("ADMIN_USER", "admin")
    ADMIN_PASS  = env("ADMIN_PASS", "admin")
    ADMIN_EMAIL = env("ADMIN_EMAIL", "admin@example.com")

    # ── 1xPanel Provider ──
    PROVIDER_URL = env("PROVIDER_URL", "https://1xpanel.com/api/v2")
    PROVIDER_KEY = env("PROVIDER_KEY", "")

    # ── To'lov tizimlari ──
    PAYME_ID       = env("PAYME_ID", "")
    PAYME_KEY      = env("PAYME_KEY", "")
    CLICK_MERCHANT = env("CLICK_MERCHANT", "")
    CLICK_SERVICE  = env("CLICK_SERVICE", "")
    CLICK_SECRET   = env("CLICK_SECRET", "")

    # ── USDT / Crypto ──
    USDT_WALLET = env("USDT_WALLET", "")

    # ── Telegram bot ──
    BOT_TOKEN     = env("BOT_TOKEN", "")
    ADMIN_CHAT_ID = env("ADMIN_CHAT_ID", "")