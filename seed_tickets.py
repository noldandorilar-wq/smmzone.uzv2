"""
O'zbekcha soxta support tiketlar - avto-moslashadigan versiya
Jadval strukturasini avtomatik aniqlaydi
"""
import sys, os, sqlite3, random
from datetime import datetime, timedelta
sys.path.insert(0, os.getcwd())
from config import Config

TICKET_SUBJECTS = [
    "Order bajarilmadi", "Pul yechilmadi", "Like'lar kelmayapti",
    "Followers tushib ketdi", "Tolov qabul qilinmadi", "Karta tasdiqlanmadi",
    "Refill kerak", "Order tezroq bajarilsinmi?", "Hisobimga kira olmayapman",
    "Parol unutdim", "Balansim notog'ri", "Click orqali tolov ishlamadi",
    "Payme orqali tolov muammosi", "Yangi xizmat qo'shasizmi?",
    "Narxlar qachon tushadi?", "Promokod ishlamadi", "Order Pending'da turibdi",
    "Order Cancelled bo'ldi pul qaytmadi", "Saytga kirib bo'lmayapti",
    "Telegram kanaliga subscriber kerak", "Instagram view'lar tushib qoldi",
    "TikTok like'lar kelmayapti", "Youtube subscriberlar yo'qoldi",
    "API key qayerdan olaman?", "Referal pulim qachon keladi?",
    "Order ID topilmayapti", "Hisobni o'chirib bering", "Hamkorlik haqida",
    "Reklama qilmoqchiman", "Boshqa savol bor",
]

USER_MESSAGES = [
    "Salom, men 2 kun oldin order berdim, hali ham bajarilmadi. Iltimos tekshirib bering.",
    "Assalomu alaykum, balansimga 50 ming so'm tushirdim, lekin hisobimda ko'rinmayapti.",
    "Aka order ID berganman, like'lar kelmayapti. Pulim qaytadimi?",
    "Salom, instagram followers olganman, lekin yarmi tushib ketdi. Refill kerak.",
    "Pul yubordim Click orqali, tasdiqlanmadi. Skrinshot yuborayinmi?",
    "Hurmatli admin, mening orderim 3 kundir Pending statusida. Nima sababdan?",
    "Karta orqali to'lov qildim, lekin hech qanday javob yo'q. Iltimos tekshiring.",
    "Salom! Saytingiz juda yaxshi, lekin TikTok like narxi yuqori.",
    "Aka, parol unutdim. Telefon raqamim orqali tiklab bering iltimos.",
    "Salom, men sizning sayt orqali ko'p order beraman. VIP narx mumkinmi?",
    "Order bergandan keyin pulim yechildi lekin like kelmadi. Help.",
    "Telegram subscriber olganman 1000ta, lekin 800tasi tushib ketdi.",
    "Hurmatli admin, hisobimga kira olmayapman. Login kiritsam noto'g'ri parol deydi.",
    "Salom, men api ulamoqchiman. Hujjatlar bormi?",
    "Yutubga subscriber kerak edi, hech qanday paket yo'qmi?",
    "Promokod WELCOME20 ishlamayapti, expire bo'lganmi?",
    "Salom, narxlar qachon arzonlashadi? Raqibda arzonroq.",
    "Iltimos orderni tezroq bajarib bering, urgent kerak.",
    "Pul tushirdim 30 daqiqadan beri kutyapman.",
    "Akajon, refill tugmasi yo'q, qanday qilaman?",
]

START = datetime(2025, 1, 1)
END = datetime(2026, 5, 5)

def rdate(start=None):
    s = start or START
    secs = int((END - s).total_seconds())
    if secs <= 0:
        return s
    return s + timedelta(seconds=random.randint(0, secs))


print("=" * 60)
print("  Support tiketlar yaratilmoqda...")
print("=" * 60)

db = sqlite3.connect(Config.DB_PATH)
db.row_factory = sqlite3.Row

# Qaysi jadvalni ishlatishni aniqlash
target_table = None
for tname in ["support_tickets", "tickets"]:
    exists = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tname,)
    ).fetchone()
    if exists:
        target_table = tname
        break

if not target_table:
    print("XATO: tickets jadvali topilmadi!")
    sys.exit()

# Jadval ustunlarini olish
columns = [r[1] for r in db.execute(f"PRAGMA table_info({target_table})").fetchall()]
print(f"\nJadval: {target_table}")
print(f"Ustunlar: {columns}")

def find_col(possible_names, columns):
    for name in possible_names:
        if name in columns:
            return name
    return None

col_user_id  = find_col(["user_id", "uid"], columns)
col_subject  = find_col(["subject", "title", "topic"], columns)
col_message  = find_col(["message", "content", "body", "text", "description"], columns)
col_status   = find_col(["status", "state"], columns)
col_priority = find_col(["priority", "level"], columns)
col_created  = find_col(["created_at", "created", "date_created"], columns)
col_updated  = find_col(["updated_at", "updated", "date_updated"], columns)

print(f"\nMoslashtirildi:")
print(f"  user_id : {col_user_id}")
print(f"  subject : {col_subject}")
print(f"  message : {col_message}")
print(f"  status  : {col_status}")

if not col_user_id or not col_subject or not col_message:
    print("\nXATO: Kerakli ustunlar yo'q!")
    print("Jadval ustunlari ro'yxatini menga yuboring.")
    sys.exit()

# Userlar
users = db.execute(
    "SELECT id, created_at FROM users WHERE role='user' ORDER BY RANDOM() LIMIT 3000"
).fetchall()

if not users:
    print("XATO: Userlar yo'q!")
    sys.exit()

# Dinamik SQL
insert_cols = [col_user_id, col_subject, col_message]
if col_status:   insert_cols.append(col_status)
if col_priority: insert_cols.append(col_priority)
if col_created:  insert_cols.append(col_created)
if col_updated:  insert_cols.append(col_updated)

placeholders = ",".join(["?"] * len(insert_cols))
sql = f"INSERT INTO {target_table} ({','.join(insert_cols)}) VALUES ({placeholders})"

print(f"\nSQL: {sql}")
print(f"\n1500 ta tiket yaratilmoqda...")

STATUSES = ["open", "pending", "answered", "closed"]
PRIORITIES = ["low", "normal", "high", "urgent"]

ticket_batch = []
for i in range(1500):
    user = random.choice(users)
    user_date = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
    created = rdate(user_date)
    updated = created + timedelta(hours=random.randint(1, 72))
    if updated > END:
        updated = END

    row = [
        user["id"],
        random.choice(TICKET_SUBJECTS),
        random.choice(USER_MESSAGES),
    ]
    if col_status:
        row.append(random.choices(STATUSES, weights=[20, 15, 35, 30])[0])
    if col_priority:
        row.append(random.choices(PRIORITIES, weights=[20, 60, 15, 5])[0])
    if col_created:
        row.append(created.strftime("%Y-%m-%d %H:%M:%S"))
    if col_updated:
        row.append(updated.strftime("%Y-%m-%d %H:%M:%S"))

    ticket_batch.append(tuple(row))

    if (i + 1) % 300 == 0:
        print(f"   {i+1}/1500")

db.executemany(sql, ticket_batch)
db.commit()
print("   Tayyor!")

total = db.execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]
print("\n" + "=" * 60)
print(f"  TAYYOR! Jami tiketlar: {total:,}")
print("=" * 60)

db.close()