import json
import asyncio
import os
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

from services.spx_api import get_tracking

TOKEN = "6324314072:AAEvtX9ROY4SA8DUKMkhLpm2_77IJbEsT6M"#os.getenv("TOKEN")  # 🔥 dùng env (Railway)

DATA_FILE = "data/orders.json"
USERS_FILE = "data/users.json"


# ===== STORAGE =====
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return []


def save_json(path, data):
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_orders():
    return load_json(DATA_FILE)


def save_orders(data):
    save_json(DATA_FILE, data)


def load_users():
    return load_json(USERS_FILE)


def save_users(data):
    save_json(USERS_FILE, data)


# ===== UTIL =====
def format_time(epoch):
    return datetime.fromtimestamp(epoch).strftime("%H:%M %d/%m")


def build_timeline(records):
    msg = "📍 Hành trình đơn hàng:\n\n"
    reversed_records = list(reversed(records[:5]))

    for i, r in enumerate(reversed_records):
        time = format_time(r["actual_time"])
        title = r["buyer_description"]

        if i == len(reversed_records) - 1:
            msg += f"🟢 {time}\n🔥 {title}\n\n"
        else:
            msg += f"⚪ {time}\n{title}\n\n"

    return msg


# ===== MENU =====
def main_menu():
    keyboard = [
        ["➕ Thêm đơn"],
        ["📦 Xem đơn"],
        ["🌐 Mở web"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

    await update.message.reply_text(
        "📦 Tracking Bot",
        reply_markup=main_menu()
    )


# ===== ADD FLOW =====
async def add_order_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nhập: CODE NOTE")
    context.user_data["adding"] = True


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ADD FLOW
    if context.user_data.get("adding"):
        if " " not in text:
            await update.message.reply_text("❌ Format: CODE NOTE")
            return

        code, note = text.split(" ", 1)

        orders = load_orders()
        orders.append({"code": code, "note": note})
        save_orders(orders)

        context.user_data["adding"] = False

        await update.message.reply_text("✅ Đã thêm", reply_markup=main_menu())
        return

    # MENU
    if text == "➕ Thêm đơn":
        await add_order_prompt(update, context)

    elif text == "📦 Xem đơn":
        await list_orders(update, context)

    elif text == "🌐 Mở web":
        await update.message.reply_text(
            "👉 https://your-app.up.railway.app"
        )


# ===== LIST =====
async def list_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = load_orders()

    if not orders:
        await update.message.reply_text("📭 Chưa có đơn")
        return

    keyboard = []
    for i, o in enumerate(orders):
        keyboard.append([
            InlineKeyboardButton(
                f"{o['note']} ({o['code'][:6]}...)",
                callback_data=f"view_{i}"
            ),
            InlineKeyboardButton("❌", callback_data=f"delete_{i}")
        ])

    await update.message.reply_text(
        "📦 Danh sách:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===== BUTTON =====
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    orders = load_orders()
    data = query.data

    # VIEW
    if data.startswith("view_"):
        idx = int(data.split("_")[1])

        if idx >= len(orders):
            await query.edit_message_text("❌ Không tồn tại")
            return

        order = orders[idx]

        try:
            api = get_tracking(order["code"])
            records = api["data"]["sls_tracking_info"]["records"]
        except:
            await query.edit_message_text("❌ Lỗi tracking")
            return

        msg = f"📦 {order['note']}\n{order['code']}\n\n"
        msg += build_timeline(records)

        await query.edit_message_text(msg)

    # DELETE
    elif data.startswith("delete_"):
        idx = int(data.split("_")[1])

        if idx >= len(orders):
            await query.edit_message_text("❌ Không tồn tại")
            return

        removed = orders.pop(idx)
        save_orders(orders)

        await query.edit_message_text(f"🗑 Đã xoá {removed['note']}")


# ===== BACKGROUND =====
async def check_updates(app):
    while True:
        orders = load_orders()
        users = load_users()
        changed = False

        for o in orders:
            try:
                data = get_tracking(o["code"])
                records = data["data"]["sls_tracking_info"]["records"]

                latest = records[0]
                latest_time = latest["actual_time"]

                if "last_time" not in o:
                    o["last_time"] = latest_time
                    changed = True
                    continue

                if latest_time > o["last_time"]:
                    o["last_time"] = latest_time
                    changed = True

                    msg = f"📦 {o['note']}\n{o['code']}\n\n"
                    msg += f"🔔 {latest['buyer_description']}"

                    for uid in users:
                        await app.bot.send_message(uid, msg)

            except Exception as e:
                print("ERROR:", e)

        if changed:
            save_orders(orders)

        await asyncio.sleep(60)


async def post_init(app):
    print("🚀 Bot running...")
    app.create_task(check_updates(app))
    


# ===== RUN =====

def start_bot():
 app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

 app.add_handler(CommandHandler("start", start))
 app.add_handler(CommandHandler("list", list_orders))
 app.add_handler(CallbackQueryHandler(handle_button))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

 app.run_polling()
 
start_bot()
app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
