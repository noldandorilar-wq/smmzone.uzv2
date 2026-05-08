from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from database.db import get_db

support_bp = Blueprint("support", __name__)

@support_bp.route("/support")
def support_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    db = get_db()
    tickets = db.execute(
        "SELECT t.*, u.username FROM tickets t "
        "JOIN users u ON u.id=t.user_id "
        "WHERE t.user_id=? ORDER BY t.created_at DESC",
        (session["user_id"],)
    ).fetchall()
    return render_template("support.html", tickets=tickets)

@support_bp.route("/support/new", methods=["POST"])
def support_new():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    if not subject or not message:
        flash("Mavzu va xabar to'ldirilishi shart", "error")
        return redirect(url_for("support.support_page"))
    db = get_db()
    cur = db.execute(
        "INSERT INTO tickets (user_id, subject) VALUES (?, ?)",
        (session["user_id"], subject)
    )
    ticket_id = cur.lastrowid
    db.execute(
        "INSERT INTO ticket_messages (ticket_id, user_id, message) VALUES (?, ?, ?)",
        (ticket_id, session["user_id"], message)
    )
    db.commit()
    flash("Savolingiz yuborildi!", "success")
    return redirect(url_for("support.support_page"))

@support_bp.route("/admin/support")
def admin_support():
    if session.get("role") != "admin":
        return redirect(url_for("user.dashboard"))
    db     = get_db()
    status = request.args.get("status", "")
    if status:
        tickets = db.execute(
            "SELECT t.*, u.username FROM tickets t "
            "JOIN users u ON u.id=t.user_id "
            "WHERE t.status=? ORDER BY t.created_at DESC", (status,)
        ).fetchall()
    else:
        tickets = db.execute(
            "SELECT t.*, u.username FROM tickets t "
            "JOIN users u ON u.id=t.user_id "
            "ORDER BY t.created_at DESC"
        ).fetchall()
    return render_template("admin_support.html", tickets=tickets)

@support_bp.route("/admin/support/reply", methods=["POST"])
def admin_reply():
    if session.get("role") != "admin":
        return redirect(url_for("user.dashboard"))
    ticket_id = request.form.get("ticket_id")
    reply     = request.form.get("reply", "").strip()
    if not ticket_id or not reply:
        flash("Javob bo'sh bo'lishi mumkin emas", "error")
        return redirect(url_for("support.admin_support"))
    db = get_db()
    db.execute(
        "INSERT INTO ticket_messages (ticket_id, user_id, message, is_admin) VALUES (?, ?, ?, 1)",
        (ticket_id, session["user_id"], reply)
    )
    db.execute("UPDATE tickets SET status='answered' WHERE id=?", (ticket_id,))
    db.commit()
    flash("Javob yuborildi!", "success")
    return redirect(url_for("support.admin_support"))

@support_bp.route("/admin/support/close/<int:ticket_id>", methods=["POST"])
def admin_close(ticket_id):
    if session.get("role") != "admin":
        return redirect(url_for("user.dashboard"))
    db = get_db()
    db.execute("UPDATE tickets SET status='closed' WHERE id=?", (ticket_id,))
    db.commit()
    flash("Tiket yopildi", "success")
    return redirect(url_for("support.admin_support"))