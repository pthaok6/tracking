import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from services.db import *
from services.spx_api import get_tracking

TOKEN = "YOUR_TOKEN"

async def start(update, context):
    await update.message.reply_text("Bot tracking ready")

async def check_updates(app):
    while True:
        orders = get_orders()

        for o in orders:
            try:
                data = get_tracking(o["code"])
                records = data["data"]["sls_tracking_info"]["records"]

                latest = records[0]["actual_time"]

                if not o["last_time"] or latest > o["last_time"]:
                    update_time(o["id"], latest, o["seen_time"])

                    msg = f"📦 {o['note']}\n{o['code']}\n🔔 Update mới"

                    for uid in app.bot_data.get("users", []):
                        await app.bot.send_message(uid, msg)

            except:
                pass

        await asyncio.sleep(60)

async def post_init(app):
    app.create_task(check_updates(app))

app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()