import os
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# लॉग सेटअप
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# बॉट टोकन और डिफ़ॉल्ट टार्गेट चैट आईडी
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# चैट ID सेट करने का कमांड
async def set_target_chat(update: Update, context: CallbackContext):
    global TARGET_CHAT_ID
    TARGET_CHAT_ID = str(update.message.chat_id)
    os.environ["TARGET_CHAT_ID"] = TARGET_CHAT_ID
    await update.message.reply_text(f"✅ Target Chat ID सेट कर दिया गया: `{TARGET_CHAT_ID}`")

# फॉरवर्ड करने का फंक्शन
async def forward_messages(update: Update, context: CallbackContext):
    global TARGET_CHAT_ID
    chat_id = update.message.chat_id
    text = update.message.text.split()

    if len(text) < 3:
        await update.message.reply_text("❌ कृपया पहले और आखिरी मेसेज का लिंक भेजें।\nउदाहरण: /forward first_link last_link")
        return

    first_msg_id = int(text[1].split("/")[-1])
    last_msg_id = int(text[2].split("/")[-1])
    from_chat_id = chat_id

    if not TARGET_CHAT_ID:
        await update.message.reply_text("❌ पहले /setchat कमांड से टार्गेट चैट सेट करें!")
        return

    for msg_id in range(first_msg_id + 1, last_msg_id):
        try:
            await bot.forward_message(chat_id=TARGET_CHAT_ID, from_chat_id=from_chat_id, message_id=msg_id)
        except Exception as e:
            logging.error(f"⚠️ फ़ॉरवर्ड करने में दिक्कत: {e}")

    await update.message.reply_text("✅ सभी मेसेज सफलतापूर्वक फॉरवर्ड कर दिए गए!")

# बॉट सेटअप
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("setchat", set_target_chat))  # चैट सेट करने का कमांड
    app.add_handler(CommandHandler("forward", forward_messages))  # फॉरवर्ड करने का कमांड

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
