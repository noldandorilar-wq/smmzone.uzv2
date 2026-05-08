import os

def env(key, default=""):
    return os.environ.get(key, default)

class Config:
    SECRET_KEY     = env("SECRET_KEY", "change-me-in-production")
    SITE_NAME      = env("SITE_NAME", "SMMZONE")
    PORT           = int(env("PORT", "8000"))
    DB_PATH        = env("DB_PATH", "smm_panel.db")

    ADMIN_USER     = env("ADMIN_USER", "admin")
    ADMIN_PASS     = env("ADMIN_PASS", "admin")
    ADMIN_EMAIL    = env("ADMIN_EMAIL", "admin@example.com")

    MIN_DEPOSIT    = int(env("MIN_DEPOSIT", "5000"))

    PROVIDER_URL   = env("PROVIDER_URL", "https://1xpanel.com/api/v2")
    PROVIDER_KEY   = env("PROVIDER_KEY", "")

    PAYME_ID       = env("PAYME_ID", "")
    PAYME_KEY      = env("PAYME_KEY", "")
    PAYME_URL      = env("PAYME_URL", "https://checkout.paycom.uz")

    CLICK_MERCHANT = env("CLICK_MERCHANT", "")
    CLICK_SERVICE  = env("CLICK_SERVICE", "")
    CLICK_SECRET   = env("CLICK_SECRET", "")
    CLICK_KEY      = env("CLICK_KEY", "")

    USDT_WALLET    = env("USDT_WALLET", "")
    TRONGRID_KEY   = env("TRONGRID_KEY", "")

    BOT_TOKEN      = env("BOT_TOKEN", "")
    ADMIN_CHAT_ID  = env("ADMIN_CHAT_ID", "")