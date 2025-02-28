import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Watermark function
def add_watermark(input_video, output_video, watermark_text):
    video = VideoFileClip(input_video)
    txt_clip = TextClip(watermark_text, fontsize=50, color='white', font='Arial')
    txt_clip = txt_clip.set_position(('center')).set_duration(video.duration)
    final_video = CompositeVideoClip([video, txt_clip])
    final_video.write_videofile(output_video, codec='libx264')

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome! Send me a video and the watermark text.')

# Handle video and text
def handle_video(update: Update, context: CallbackContext):
    # Download video
    video_file = update.message.video.get_file()
    video_file.download('input.mp4')
    
    # Get watermark text
    watermark_text = update.message.caption
    
    # Add watermark
    add_watermark('input.mp4', 'output.mp4', watermark_text)
    
    # Send output video
    update.message.reply_video(video=open('output.mp4', 'rb'))
    
    # Clean up
    os.remove('input.mp4')
    os.remove('output.mp4')

# Main function
def main():
    # Telegram bot token
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Start the bot
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    
    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
