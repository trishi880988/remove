import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a video and I'll add a watermark.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    video_path = "input.mp4"
    await file.download_to_drive(video_path)

    await update.message.reply_text("Send the watermark text you want on the video.")
    context.user_data['video_path'] = video_path

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = update.message.text
    video_path = context.user_data.get("video_path")
    
    if not video_path:
        await update.message.reply_text("Please send a video first.")
        return

    output_video = "output.mp4"
    await update.message.reply_text("Processing your video...")

    start_time = time.time()
    add_watermark(video_path, output_video, watermark_text)
    processing_time = time.time() - start_time

    await update.message.reply_text(f"Video processed in {processing_time:.2f} seconds!")
    await update.message.reply_video(video=open(output_video, 'rb'))

    os.remove(video_path)
    os.remove(output_video)

def add_watermark(input_video, output_video, watermark_text):
    video = VideoFileClip(input_video)
    txt_clip = TextClip(watermark_text, fontsize=50, color='white', font='Arial').set_position(('center', 'bottom')).set_duration(video.duration)
    final_video = CompositeVideoClip([video, txt_clip])
    final_video.write_videofile(output_video, codec='libx264')

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == "__main__":
    main()
