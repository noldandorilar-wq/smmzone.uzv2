import sys, os
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, redirect, url_for, session, request, jsonify, render_template

from config import Config
from database.db import get_db, close_db
from database.migrate import init_db

from services.balance_service import balance_bp
from auth.login import auth_bp
from services.user_service import user_bp
from services.admin_service import admin_bp
from api.routes import api_bp
from support_service import support_bp
from services.payment_service import payme_webhook, click_prepare, click_complete


# ─── APP ─────────────────────────────
app = Flask(__name__,
            template_folder="templates",
            static_folder="static")

app.secret_key = Config.SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

app.teardown_appcontext(close_db)


# ─── BLUEPRINTS ─────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(support_bp)
app.register_blueprint(balance_bp)


# ─── ROUTES ─────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("user.dashboard"))
    return render_template("index.html")


@app.route("/store")
def store():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

    plans = {
        "premium_1m": {"name": "Premium 1 Oy",  "months": 1,  "price": 85_000},
        "premium_3m": {"name": "Premium 3 Oy",  "months": 3,  "price": 230_000},
        "premium_6m": {"name": "Premium 6 Oy",  "months": 6,  "price": 420_000},
        "premium_12m":{"name": "Premium 12 Oy", "months": 12, "price": 750_000},
    }

    stars_price = 490  # 1 Star narxi (so'm)

    pubg_prices = [
        {"uc": 60,    "price": 15_000},
        {"uc": 325,   "price": 75_000},
        {"uc": 660,   "price": 145_000},
        {"uc": 1800,  "price": 380_000},
        {"uc": 3850,  "price": 750_000},
        {"uc": 8100,  "price": 1_500_000},
    ]

    return render_template("store.html",
                           user=user,
                           plans=plans,
                           stars_price=stars_price,
                           pubg_prices=pubg_prices)


@app.route("/api-docs")
def api_docs():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template("api.html", user=user)


# ─── WEBHOOKS ───────────────────────
@app.route("/api/webhook/payme", methods=["POST"])
def payme_wh():
    return jsonify(payme_webhook(request.get_json() or {}))


@app.route("/api/webhook/click/prepare", methods=["POST"])
def click_prep():
    return jsonify(click_prepare(request.form.to_dict()))


@app.route("/api/webhook/click/complete", methods=["POST"])
def click_comp():
    return jsonify(click_complete(request.form.to_dict()))


# ─── CONTEXT PROCESSOR ──────────────
@app.context_processor
def inject_globals():
    user_balance = 0

    if "user_id" in session:
        db = get_db()
        u = db.execute(
            "SELECT balance FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()

        if u:
            user_balance = u["balance"]

        session["balance"] = user_balance

    return {
        "site_name": Config.SITE_NAME,
        "user_balance": user_balance
    }


# ─── ERROR HANDLERS ─────────────────
@app.errorhandler(404)
def e404(e):
    return render_template("index.html"), 404


@app.errorhandler(403)
def e403(e):
    return jsonify({"error": "Ruxsat yo'q"}), 403


# ─── AUTO SYNC ──────────────────────
def start_auto_sync():
    import threading, time

    def loop():
        while True:
            time.sleep(300)
            try:
                from services.order_service import sync_all_active
                sync_all_active()
            except Exception as e:
                print("Auto-sync error:", e)

    threading.Thread(target=loop, daemon=True).start()


# ─── INIT ───────────────────────────
init_db()
start_auto_sync()


# ─── AUTO CREATE ADMIN ───────────────
with app.app_context():
    from utils.security import hash_pw, gen_key, gen_ref
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not existing:
        db.execute(
            "INSERT INTO users (username, email, password, role, is_active, api_key, ref_code, balance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("admin", "admin@admin.com", hash_pw("admin123"), "admin", 1, gen_key(), gen_ref(), 0)
        )
        db.commit()
        print("Admin yaratildi!")


# ─── MAIN ───────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=False)