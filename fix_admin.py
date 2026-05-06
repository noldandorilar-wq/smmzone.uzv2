from main import app
from database.db import get_db
from utils.security import hash_pw

with app.app_context():
    db = get_db()
    db.execute(
        "UPDATE users SET password=? WHERE username='admin'",
        (hash_pw("123456"),)
    )
    db.commit()
    print("ADMIN FIXED")