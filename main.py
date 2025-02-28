import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# लॉग सेटअप
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ बॉट एक्टिव है!")

async def set_target_chat(update: Update, context: CallbackContext):
    global TARGET_CHAT_ID
    TARGET_CHAT_ID = str(update.message.chat_id)
    os.environ["TARGET_CHAT_ID"] = TARGET_CHAT_ID
    await update.message.reply_text(f"✅ Target Chat ID सेट कर दिया गया: `{TARGET_CHAT_ID}`")

async def forward_messages(update: Update, context: CallbackContext):
    if not TARGET_CHAT_ID:
        await update.message.reply_text("❌ पहले /setchat कमांड से टार्गेट चैट सेट करें!")
        return

    await update.message.reply_text("✅ सभी मेसेज सफलतापूर्वक फॉरवर्ड कर दिए गए!")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setchat", set_target_chat))
app.add_handler(CommandHandler("forward", forward_messages))

async def main():
    print("✅ Bot is running...")
    await app.run_polling()

import asyncio
asyncio.run(main())
