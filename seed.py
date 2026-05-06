import sys, os, sqlite3, hashlib, secrets, random
from datetime import datetime, timedelta
sys.path.insert(0, os.getcwd())
from config import Config

NAMES = ['azizbek','sherzod','bobur','temur','jasur','sardor','akmal','alisher',
         'anvar','asadbek','bahrom','behzod','bekzod','bilol','botir','diyor',
         'doniyor','davron','dilshod','elyor','elbek','farhod','farrux','feruz',
         'firdavs','hasan','husan','habib','ibrohim','iskandar','islom','ilxom',
         'ismoil','jamshid','javohir','kamol','komil','karim','muhammad','mansur',
         'muzaffar','nodir','nurbek','otabek','oybek','ozodbek','rustam','rasul',
         'ravshan','sherali','shoxrux','suxrob','sirojiddin','umar','usmon',
         'xurshid','yusufbek','zafar','zokir','ziyodullo','ahror','ahmad','akbar',
         'amir','asilbek','aybek','baxtiyor','boburjon','davlat','elnur',
         'fazliddin','fayzullo','jaloliddin','javlon','jahongir','kamron',
         'muhammadali','mirsaid','nuriddin','olimjon','qodir','qudrat',
         'rahmatullo','toshbek','umid','xolmurod','yoldosh','ahmadjon']

DOMAINS = ['gmail.com','mail.ru','yandex.com','inbox.uz','umail.uz']
METHODS = ['Karta','Click','Payme','Uzum']
STATUSES = ['Completed']*8 + ['Pending','Processing','Cancelled']

START = datetime(2025, 1, 1)
END = datetime(2026, 5, 5)

def rdate(start=None):
    s = start or START
    secs = int((END - s).total_seconds())
    if secs <= 0:
        return s
    return s + timedelta(seconds=random.randint(0, secs))

print("=" * 60)
print("  Soxta foydalanuvchilar yaratilmoqda...")
print("=" * 60)

db = sqlite3.connect(Config.DB_PATH)
db.row_factory = sqlite3.Row

services = db.execute(
    "SELECT id, price_per_1000, min_order, max_order FROM services WHERE is_active=1"
).fetchall()
if not services:
    print("XATO: Avval xizmatlarni import qiling!")
    sys.exit()

used = set(r[0] for r in db.execute("SELECT username FROM users").fetchall())

# 1) USERLAR
print("\nUserlar yaratilmoqda...")
ub = []
for i in range(10000):
    while True:
        u = random.choice(NAMES) + str(random.randint(1, 9999))
        if u not in used:
            used.add(u)
            break
    ub.append((
        u,
        u + "@" + random.choice(DOMAINS),
        hashlib.sha256(secrets.token_hex(8).encode()).hexdigest(),
        "user",
        secrets.token_hex(16),
        secrets.token_hex(4).upper(),
        random.choice([0, 0, 0, 5000, 12000, 25000, 50000, 100000, 200000]),
        random.choices([1, 0], weights=[95, 5])[0],
        rdate().strftime("%Y-%m-%d %H:%M:%S")
    ))
    if (i + 1) % 2000 == 0:
        print("   " + str(i + 1) + "/10000")

db.executemany(
    "INSERT INTO users (username,email,password,role,api_key,ref_code,balance,is_active,created_at) "
    "VALUES (?,?,?,?,?,?,?,?,?)", ub
)
db.commit()
print("   Userlar tayyor!")

uids = db.execute(
    "SELECT id, created_at FROM users WHERE role='user' ORDER BY id DESC LIMIT 10000"
).fetchall()
udata = [(r["id"], datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S")) for r in uids]

# 2) ORDERLAR
print("\nOrderlar yaratilmoqda...")
ob = []
for i in range(25000):
    uid, udate = random.choice(udata)
    s = random.choice(services)
    q = random.randint(s["min_order"], min(s["max_order"], s["min_order"] * 100))
    p = round((q / 1000) * s["price_per_1000"], 2)
    odate = rdate(udate)
    ob.append((
        uid, s["id"],
        "https://instagram.com/p/" + secrets.token_hex(5),
        q, p, random.choice(STATUSES),
        odate.strftime("%Y-%m-%d %H:%M:%S")
    ))
    if (i + 1) % 5000 == 0:
        print("   " + str(i + 1) + "/25000")

db.executemany(
    "INSERT INTO orders (user_id,service_id,link,quantity,price,status,created_at) "
    "VALUES (?,?,?,?,?,?,?)", ob
)
db.commit()
print("   Orderlar tayyor!")

# 3) TOLOVLAR
print("\nTolovlar yaratilmoqda...")
dp = []
for i in range(6000):
    uid, udate = random.choice(udata)
    amt = random.choice([5000, 10000, 20000, 30000, 50000, 100000, 150000, 250000, 500000])
    st = random.choices(["completed", "pending", "rejected"], weights=[85, 10, 5])[0]
    ddate = rdate(udate)
    ds = ddate.strftime("%Y-%m-%d %H:%M:%S")
    dp.append((
        uid, amt, random.choice(METHODS), st,
        "TX" + str(random.randint(100000, 999999)),
        ds, ds if st == "completed" else None
    ))

db.executemany(
    "INSERT INTO deposits (user_id,amount,method,status,tx_hash,created_at,confirmed_at) "
    "VALUES (?,?,?,?,?,?,?)", dp
)
db.commit()

print("\n" + "=" * 60)
print("  TAYYOR!")
print("=" * 60)
print("  Jami userlar:   " + str(db.execute("SELECT COUNT(*) FROM users").fetchone()[0]))
print("  Jami orderlar:  " + str(db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]))
print("  Jami tolovlar:  " + str(db.execute("SELECT COUNT(*) FROM deposits").fetchone()[0]))
print("=" * 60)
db.close()