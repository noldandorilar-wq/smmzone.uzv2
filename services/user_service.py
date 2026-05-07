"""User va balans boshqaruv blueprint (FIXED VERSION)"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from database.db import get_db, r2d, r2l
from services.order_service import place_order, sync_all_active
from auth.auth_middleware import login_required
from services.payment_service import payme_create, usdt_create, usdt_check
from utils.security import gen_key
from config import Config

user_bp = Blueprint("user", __name__)


# ─────────────────────────────
# SAFE USER HELPER
# ─────────────────────────────
def current_user():
    db = get_db()
    user_id = session.get("user_id")
    if not user_id:
        return None
    row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@user_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    u = current_user()
    if not u:
        return redirect(url_for("auth.login_page"))

    stats = {
        "total_orders": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=?", (u["id"],)
        ).fetchone()[0],
        "completed": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=? AND status='Completed'", (u["id"],)
        ).fetchone()[0],
        "pending": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=? AND status IN ('Pending','Processing')", (u["id"],)
        ).fetchone()[0],
        "total_spent": u.get("total_spent", 0),
    }

    recent = r2l(db.execute(
        "SELECT o.*, s.name as svc_name FROM orders o "
        "JOIN services s ON o.service_id=s.id "
        "WHERE o.user_id=? ORDER BY o.created_at DESC LIMIT 5",
        (u["id"],)
    ).fetchall())

    return render_template("dashboard.html", user=u, stats=stats, recent=recent)


# ─────────────────────────────
# NEW ORDER
# ─────────────────────────────
@user_bp.route("/new-order", methods=["GET", "POST"])
@login_required
def new_order():
    db = get_db()
    u = current_user()
    if not u:
        return redirect(url_for("auth.login_page"))

    cats = r2l(db.execute(
        "SELECT * FROM categories WHERE is_active=1 ORDER BY sort_order"
    ).fetchall())

    svcs = r2l(db.execute(
        "SELECT s.*, c.name as cat_name FROM services s "
        "JOIN categories c ON s.category_id=c.id "
        "WHERE s.is_active=1 ORDER BY c.sort_order, s.id"
    ).fetchall())

    if request.method == "POST":
        svc_id = int(request.form.get("service_id", 0))
        link = request.form.get("link", "").strip()
        qty = int(request.form.get("quantity", 0))

        result = place_order(svc_id, link, qty)

        if result.get("ok"):
            flash(f"✅ Order #{result['order_id']} yaratildi!", "success")
            return redirect(url_for("user.orders"))

        flash(result.get("error", "Xato yuz berdi"), "error")

    return render_template("new_order.html", user=u, categories=cats, services=svcs)


# ─────────────────────────────
# ORDERS
# ─────────────────────────────
@user_bp.route("/orders")
@login_required
def orders():
    db = get_db()
    u = current_user()
    if not u:
        return redirect(url_for("auth.login_page"))

    page = max(1, int(request.args.get("page", 1)))
    status = request.args.get("status", "")

    limit = 20
    where = "WHERE o.user_id=?"
    params = [u["id"]]

    if status:
        where += " AND o.status=?"
        params.append(status)

    rows = r2l(db.execute(
        f"SELECT o.*, s.name as svc_name FROM orders o "
        f"JOIN services s ON o.service_id=s.id "
        f"{where} ORDER BY o.created_at DESC LIMIT ? OFFSET ?",
        params + [limit, (page - 1) * limit]
    ).fetchall())

    total = db.execute(
        f"SELECT COUNT(*) FROM orders o {where}", params
    ).fetchone()[0]

    return render_template(
        "orders.html",
        user=u,
        orders=rows,
        page=page,
        total=total,
        limit=limit,
        status=status
    )


# ─────────────────────────────
# PROFILE
# ─────────────────────────────
@user_bp.route("/profile")
@login_required
def profile():
    db = get_db()
    u = current_user()
    if not u:
        return redirect(url_for("auth.login_page"))

    stats = {
        "total_orders": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=?", (u["id"],)
        ).fetchone()[0],
        "completed": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=? AND status='Completed'", (u["id"],)
        ).fetchone()[0],
        "pending": db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id=? AND status IN ('Pending','Processing')", (u["id"],)
        ).fetchone()[0],
        "total_spent": u.get("total_spent", 0),
    }

    txs = r2l(db.execute(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY created_at DESC LIMIT 30",
        (u["id"],)
    ).fetchall())

    return render_template("profile.html", user=u, transactions=txs, stats=stats)