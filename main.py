import sys, os
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


# ─── ROOT ───────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("user.dashboard"))
    return render_template("index.html")


# ─── CONTEXT (BANNER O‘CHIRILDI) ───
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


# ─── MAIN ───────────────────────────
if __name__ == "__main__":
    init_db()
    start_auto_sync()

    app.run(host="0.0.0.0", port=Config.PORT, debug=False)