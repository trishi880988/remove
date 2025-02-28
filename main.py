import os
import time
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Watermark function with advanced settings
def add_watermark(input_video, output_video, watermark_text):
    video = VideoFileClip(input_video)
    
    # Create watermark text
    txt_clip = TextClip(watermark_text, fontsize=50, color='white', font='Arial', stroke_color='black', stroke_width=2)
    txt_clip = txt_clip.set_position(('right', 'bottom')).set_duration(video.duration)
    
    # Combine video and watermark
    final_video = CompositeVideoClip([video, txt_clip])
    final_video.write_videofile(output_video, codec='libx264', fps=video.fps, threads=4, preset='ultrafast')

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text('👋 Welcome! Send me a video, and I will add a watermark to it.')

# Handle video
def handle_video(update: Update, context: CallbackContext):
    video_file = update.message.video.get_file()
    input_path = f"downloads/{video_file.file_id}.mp4"
    output_path = f"downloads/watermarked_{video_file.file_id}.mp4"
    
    # Create downloads folder if not exists
    os.makedirs("downloads", exist_ok=True)
    
    # Download video
    video_file.download(input_path)
    
    update.message.reply_text("✅ Video received! Send the text you want as a watermark.")
    context.user_data['video_path'] = input_path
    context.user_data['output_path'] = output_path

# Handle watermark text
def handle_text(update: Update, context: CallbackContext):
    watermark_text = update.message.text
    input_path = context.user_data.get('video_path')
    output_path = context.user_data.get('output_path')
    
    if not input_path:
        update.message.reply_text("❌ No video found! Please send a video first.")
        return
    
    update.message.reply_text("🔄 Processing your video... This may take some time.")
    
    def process_video():
        start_time = time.time()
        add_watermark(input_path, output_path, watermark_text)
        processing_time = time.time() - start_time
        
        update.message.reply_text(f'✅ Done! Processed in {processing_time:.2f} sec. Sending video...')
        
        with open(output_path, 'rb') as video_file:
            update.message.reply_video(video=video_file)
        
        os.remove(input_path)
        os.remove(output_path)
    
    thread = threading.Thread(target=process_video)
    thread.start()

# Main function
def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
