import sqlite3
from flask import g
from config import Config


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(Config.DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def execute(query, params=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    return cursor


def fetchone(query, params=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    return cursor.fetchone()


def fetchall(query, params=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()


def r2d(row):
    """sqlite3.Row ni dict ga aylantiradi"""
    return dict(row) if row else None


def r2l(rows):
    """sqlite3.Row lar ro'yxatini dict lar ro'yxatiga aylantiradi"""
    return [dict(row) for row in rows] if rows else []


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()