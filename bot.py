import json
import asyncio
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

from services.spx_api import get_tracking

# ======================
# ENV SAFE
# ======================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("Missing BOT TOKEN")


DATA_FILE = "data/orders.json"
USERS_FILE = "data/users.json"


# ======================
# JSON STORAGE
# ======================
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


# ======================
# UTIL
# ======================
def format_time(epoch):
    return datetime.fromtimestamp(epoch).strftime("%H:%M %d/%m")


def build_timeline(records):
    msg = "📍 Hành trình:\n\n"
    for r in list(reversed(records[:5])):
        msg += f"{format_time(r['actual_time'])} - {r['buyer_description']}\n\n"
    return msg


# ======================
# BOT CORE
# ======================
def main_menu():
    return ReplyKeyboardMarkup(
        [["➕ Thêm đơn"], ["📦 Xem đơn"], ["🌐 Mở web"]],
        resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = update.effective_chat.id

    if uid not in users:
        users.append(uid)
        save_users(users)

    await update.message.reply_text("📦 Tracking Bot", reply_markup=main_menu())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("adding"):
        if " " not in text:
            await update.message.reply_text("❌ CODE NOTE")
            return

        code, note = text.split(" ", 1)

        orders = load_orders()
        orders.append({"code": code, "note": note})
        save_orders(orders)

        context.user_data["adding"] = False
        await update.message.reply_text("✅ Đã thêm", reply_markup=main_menu())
        return

    if text == "➕ Thêm đơn":
        context.user_data["adding"] = True
        await update.message.reply_text("Nhập: CODE NOTE")

    elif text == "📦 Xem đơn":
        orders = load_orders()

        keyboard = [
            [
                InlineKeyboardButton(f"{o['note']}", callback_data=f"view_{i}"),
                InlineKeyboardButton("❌", callback_data=f"delete_{i}")
            ]
            for i, o in enumerate(orders)
        ]

        await update.message.reply_text(
            "📦 Danh sách",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "🌐 Mở web":
        await update.message.reply_text("https://your-app.up.railway.app")


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    orders = load_orders()
    data = q.data

    if data.startswith("view_"):
        i = int(data.split("_")[1])

        try:
            api = get_tracking(orders[i]["code"])
            records = api["data"]["sls_tracking_info"]["records"]
            msg = build_timeline(records)
            await q.edit_message_text(msg)
        except:
            await q.edit_message_text("❌ Lỗi tracking")

    elif data.startswith("delete_"):
        i = int(data.split("_")[1])
        removed = orders.pop(i)
        save_orders(orders)

        await q.edit_message_text(f"🗑 Deleted {removed['note']}")


# ======================
# RUN BOT
# ======================
def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("BOT STARTED")
    app.run_polling()
