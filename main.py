import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import asyncio

# Watermark Function
async def add_watermark(input_video, output_video, watermark_text):
    video = VideoFileClip(input_video)
    txt_clip = TextClip(watermark_text, fontsize=50, color='white', font='Arial')
    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(video.duration)
    final_video = CompositeVideoClip([video, txt_clip])
    final_video.write_videofile(output_video, codec='libx264', fps=video.fps)
    video.close()
    txt_clip.close()
    final_video.close()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a video, and I'll add a watermark to it.")

# Handle Video
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_file = await update.message.video.get_file()
    await video_file.download_to_drive("input.mp4")
    await update.message.reply_text("Send me the text you want as a watermark.")
    context.user_data['video_path'] = "input.mp4"

# Handle Text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watermark_text = update.message.text
    await update.message.reply_text("Processing video... Please wait!")
    start_time = time.time()
    
    output_video = "output.mp4"
    await asyncio.to_thread(add_watermark, context.user_data['video_path'], output_video, watermark_text)
    
    processing_time = time.time() - start_time
    await update.message.reply_text(f"Video processed in {processing_time:.2f} seconds!")
    await update.message.reply_video(video=open(output_video, 'rb'))
    
    os.remove("input.mp4")
    os.remove("output.mp4")

# Main Function
async def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
