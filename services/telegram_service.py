from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from database.db import get_db
import time, os

telegram_bp = Blueprint("telegram", __name__)

PLANS = {
    "premium_1m":  {"name": "Telegram Premium 1 Oy",   "price": 55900,  "months": 1},
    "premium_3m":  {"name": "Telegram Premium 3 Oy",   "price": 169900, "months": 3},
    "premium_6m":  {"name": "Telegram Premium 6 Oy",   "price": 209900, "months": 6},
    "premium_12m": {"name": "Telegram Premium 1 Yil",  "price": 399000, "months": 12},
}

STARS_PRICE_PER_1 = 350   # 1 star = 350 so'm
PUBG_UC_PRICES = [
    {"uc": 60,    "price": 15900},
    {"uc": 180,   "price": 45900},
    {"uc": 325,   "price": 79900},
    {"uc": 660,   "price": 155900},
    {"uc": 1800,  "price": 399900},
    {"uc": 3850,  "price": 799900},
    {"uc": 8100,  "price": 1599900},
]

def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if "user_id" not in session:
            return redirect(url_for("auth.login_page"))
        return f(*a, **kw)
    return wrap

@telegram_bp.route("/store")
@login_required
def store():
    db = get_db()
    user = db.execute("SELECT balance, username FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template("store.html",
        user=user,
        plans=PLANS,
        stars_price=STARS_PRICE_PER_1,
        pubg_prices=PUBG_UC_PRICES
    )

@telegram_bp.route("/store/buy", methods=["POST"])
@login_required
def buy():
    db      = get_db()
    user_id = session["user_id"]
    item    = request.form.get("item")       # premium_1m / stars / pubg
    qty     = int(request.form.get("qty", 1))
    tg_user = request.form.get("tg_user", "").strip()
    pubg_id = request.form.get("pubg_id", "").strip()

    # Narx hisoblash
    if item in PLANS:
        plan  = PLANS[item]
        price = plan["price"]
        desc  = f"{plan['name']} — @{tg_user}"
    elif item == "stars":
        if qty < 1 or qty > 100000:
            flash("Miqdor 1 dan 100,000 gacha bo'lishi kerak!", "error")
            return redirect(url_for("telegram.store"))
        price = qty * STARS_PRICE_PER_1
        desc  = f"Telegram Stars x{qty} — @{tg_user}"
    elif item == "pubg":
        uc_amount = int(request.form.get("uc_amount", 0))
        found = next((p for p in PUBG_UC_PRICES if p["uc"] == uc_amount), None)
        if not found:
            flash("Noto'g'ri UC miqdori", "error")
            return redirect(url_for("telegram.store"))
        price = found["price"]
        desc  = f"PUBG UC x{uc_amount} — ID: {pubg_id}"
    else:
        flash("Noto'g'ri mahsulot", "error")
        return redirect(url_for("telegram.store"))

    # Balans tekshirish
    user = db.execute("SELECT balance FROM users WHERE id=?", (user_id,)).fetchone()
    if user["balance"] < price:
        flash(f"Balansingiz yetarli emas! Kerak: {price:,.0f} so'm", "error")
        return redirect(url_for("telegram.store"))

    # Sotib olish
    db.execute("UPDATE users SET balance=balance-? WHERE id=?", (price, user_id))
    db.execute(
        "INSERT INTO orders (user_id, service_id, quantity, price, link, status, created_at) VALUES (?,?,?,?,?,?,datetime('now'))",
        (user_id, 1, qty, price, desc, "Pending")
    )
    db.execute(
        "INSERT INTO transactions (user_id, type, amount, description, status) VALUES (?,?,?,?,?)",
        (user_id, "debit", price, desc, "pending")
    )
    db.commit()
    flash(f"✅ Buyurtma qabul qilindi! {desc} — 5-30 daqiqa ichida bajariladi.", "success")
    return redirect(url_for("telegram.store"))
