import logging
import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get Telegram Bot Token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    exit()

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Welcome to the MKV to MP4 Converter Bot!\n"
        "Send me an MKV file and I'll convert it to MP4 for you."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the /help command is issued."""
    await update.message.reply_text(
        "Send an MKV video file to this chat. I will convert it to MP4 format and send it back to you.\n"
        "Supported commands:\n"
        "/start - Welcome message\n"
        "/help - This help message"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles video uploads, converts MKV to MP4."""
    message = update.message
    if not message.video and not message.document:
        await message.reply_text("Please send a video file.")
        return

    file_id = None
    file_name = None

    if message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mkv"
    elif message.document:
        if message.document.mime_type and "video" in message.document.mime_type:
            file_id = message.document.file_id
            file_name = message.document.file_name
        else:
            await message.reply_text("Please send a video file (MKV format).")
            return

    if not file_name.lower().endswith(".mkv"):
        await message.reply_text("Only .mkv files are supported for conversion. Please send an MKV file.")
        return

    new_file = await context.bot.get_file(file_id)

    # Create a temporary directory for processing files if it doesn't exist
    os.makedirs("temp", exist_ok=True)

    mkv_file_path = os.path.join("temp", f"{file_id}.mkv")
    mp4_file_path = os.path.join("temp", f"{file_id}.mp4")

    try:
        await message.reply_text("Downloading your MKV file...")
        await new_file.download_to_drive(mkv_file_path)
        logger.info(f"Downloaded file to {mkv_file_path}")

        await message.reply_text("Converting to MP4... This might take a while.")

        # FFmpeg command: -i <input> -c:v copy -c:a copy <output.mp4>
        # This attempts to copy video and audio streams without re-encoding if possible.
        # If direct copy isn't possible for some codecs, FFmpeg might re-encode.
        # For more robust conversion (but slower), you might specify codecs:
        # e.g., -c:v libx264 -c:a aac
        command = [
            "ffmpeg",
            "-i", mkv_file_path,
            "-c:v", "copy",  # Try to copy video stream
            "-c:a", "aac",   # Re-encode audio to AAC (common for MP4)
            "-strict", "experimental", # Needed for some AAC encoders
            mp4_file_path
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"FFmpeg error: {stderr.decode()}")
            # Try re-encoding video as well if copy fails
            await message.reply_text("Initial conversion failed, trying full re-encoding...")
            command = [
                "ffmpeg",
                "-i", mkv_file_path,
                "-c:v", "libx264", # Re-encode video to H.264
                "-c:a", "aac",     # Re-encode audio to AAC
                "-preset", "fast",  # Faster encoding, larger file
                "-crf", "23",       # Constant Rate Factor (quality, 18-28 is typical)
                mp4_file_path
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logger.error(f"FFmpeg full re-encoding error: {stderr.decode()}")
                await message.reply_text(f"Sorry, conversion failed. FFmpeg error: {stderr.decode()[:1000]}")
                return

        logger.info(f"Converted file to {mp4_file_path}")
        await message.reply_text("Conversion complete! Uploading your MP4 file...")

        with open(mp4_file_path, "rb") as video_file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=video_file, filename=file_name.replace(".mkv", ".mp4"))

        await message.reply_text("MP4 file sent!")

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        await message.reply_text(f"An error occurred: {e}")
    finally:
        # Clean up temporary files
        if os.path.exists(mkv_file_path):
            os.remove(mkv_file_path)
        if os.path.exists(mp4_file_path):
            os.remove(mp4_file_path)
        logger.info("Cleaned up temporary files.")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    logger.info("Bot starting...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot stopped.")

if __name__ == "__main__":
    main()
