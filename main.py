from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
from datetime import datetime

# توکن ربات تو
TOKEN = "8510051967:AAEFBy8WR04ZZ5mmcuH9_yAwallKgtsnz0o"

# دیتابیس
conn = sqlite3.connect('nesiye.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS t 
             (name TEXT, amount INTEGER, type TEXT, date TEXT)''')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ربات نسیه مغازه فعال شد!\n\n"
        "دستورات:\n"
        "/نسیه اسم مبلغ → /نسیه محمدی 150\n"
        "/تسویه اسم مبلغ → /تسویه محمدی 100\n"
        "/لیست → لیست بدهکارها\n"
        "/جزئیات اسم → تاریخچه\n"
        "/حذف اسم → پاک کردن کامل"
    )

async def nesiye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = update.message.text.split()[1:]
        name = " ".join(args[:-1]) if len(args) > 1 else args[0]
        amount = int(args[-1]) * 1000
        c.execute("INSERT INTO t VALUES (?,?,?,?)", (name, amount, "نسیه", datetime.now().strftime("%Y/%m/%d %H:%M")))
        conn.commit()
        total = c.execute("SELECT SUM(CASE WHEN type='نسیه' THEN amount ELSE -amount END) FROM t WHERE name=?", (name,)).fetchone()[0] or 0
        await update.message.reply_text(f"نسیه {name} ثبت شد\nجمع کل بدهی: {total:,} تومان")
    except:
        await update.message.reply_text("مثال: /نسیه علی 80")

async def tasvie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = update.message.text.split()[1:]
        name = " ".join(args[:-1]) if len(args) > 1 else args[0]
        amount = int(args[-1]) * 1000
        c.execute("INSERT INTO t VALUES (?,?,?,?)", (name, amount, "تسویه", datetime.now().strftime("%Y/%m/%d %H:%M")))
        conn.commit()
        total = c.execute("SELECT SUM(CASE WHEN type='نسیه' THEN amount ELSE -amount END) FROM t WHERE name=?", (name,)).fetchone()[0] or 0
        await update.message.reply_text(f"تسویه {name} ثبت شد\nمانده بدهی: {total:,} تومان")
    except:
        await update.message.reply_text("مثال: /تسویه علی 50")

async def liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c.execute("SELECT name, SUM(CASE WHEN type='نسیه' THEN amount ELSE -amount END) FROM t GROUP BY name HAVING SUM(CASE WHEN type='نسیه' THEN amount ELSE -amount END) > 0 ORDER BY 2 DESC")
    rows = c.fetchall()
    if not rows:
        await update.message.reply_text("هیچ بدهی ثبت نشده")
        return
    msg = "لیست بدهکاران:\n\n"
    for i, (name, total) in enumerate(rows, 1):
        msg += f"{i}. {name} → {total:,} تومان\n"
    await update.message.reply_text(msg)

async def jaz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = " ".join(context.args)
        c.execute("SELECT type, amount, date FROM t WHERE name=? ORDER BY rowid", (name,))
        rows = c.fetchall()
        if not rows:
            await update.message.reply_text("تراکنشی نیست")
            return
        msg = f"تاریخچه {name}:\n\n"
        for typ, amt, dt in rows:
            sign = "نسیه" if typ == "نسیه" else "تسویه"
            msg += f"• {dt} | {sign} {amt//1000} هزار\n"
        total = c.execute("SELECT SUM(CASE WHEN type='نسیه' THEN amount ELSE -amount END) FROM t WHERE name=?", (name,)).fetchone()[0] or 0
        msg += f"\nجمع کل بدهی: {total:,} تومان"
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("دستور: /جزئیات اسم مشتری")

async def hazf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = " ".join(context.args)
        c.execute("DELETE FROM t WHERE name=?", (name,))
        conn.commit()
        await update.message.reply_text(f"حساب {name} کامل حذف شد")
    except:
        await update.message.reply_text("دستور: /حذف اسم مشتری")

# راه‌اندازی ربات
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("نسیه", nesiye))
app.add_handler(CommandHandler("تسویه", tasvie))
app.add_handler(CommandHandler("لیست", liste))
app.add_handler(CommandHandler("جزئیات", jaz))
app.add_handler(CommandHandler("حذف", hazf))

print("ربات در حال اجراست...")
app.run_polling()