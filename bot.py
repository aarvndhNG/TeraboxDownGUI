import logging
import os
import subprocess
import asyncio
import httpx # For streaming downloads
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

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

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Welcome to the MKV to MP4 Converter Bot!\n"
        "Send me an MKV file and I'll convert it to MP4 for you. I now support streaming for larger files!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the /help command is issued."""
    await update.message.reply_text(
        "Send an MKV video file to this chat. I will convert it to MP4 format and send it back to you.\n"
        "Supported commands:\n"
        "/start - Welcome message\n"
        "/help - This help message"
    )

async def send_processing_feedback(context: ContextTypes.DEFAULT_TYPE, chat_id: int, stop_event: asyncio.Event):
    """Sends periodic 'typing' or 'uploading' action while processing."""
    while not stop_event.is_set():
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        except Exception as e:
            logger.warning(f"Could not send chat action: {e}")
        await asyncio.sleep(4) # Telegram chat actions last for 5 seconds

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles video uploads, converts MKV to MP4 using streaming."""
    message = update.message
    if not message.video and not message.document:
        await message.reply_text("Please send a video file.")
        return

    file_id = None
    original_file_name = None
    telegram_file_size = 0


    if message.video:
        file_id = message.video.file_id
        original_file_name = message.video.file_name or f"{file_id}.mkv"
        telegram_file_size = message.video.file_size or 0
    elif message.document:
        if message.document.mime_type and ("video" in message.document.mime_type or "matroska" in message.document.mime_type):
            file_id = message.document.file_id
            original_file_name = message.document.file_name
            telegram_file_size = message.document.file_size or 0
        else:
            await message.reply_text("Please send a video file (MKV format preferred).")
            return

    if not original_file_name.lower().endswith(".mkv"):
        await message.reply_text("Warning: File does not end with .mkv. I'll try to convert it, but MKV is preferred.")

    # Inform user about potential large file issues
    if telegram_file_size > 1 * 1024 * 1024 * 1024: # 1 GB
         await message.reply_text(
            f"This looks like a large file ({telegram_file_size / (1024**3):.2f} GB). "
            "Conversion might take a very long time or fail due to Telegram/server limits."
        )
    elif telegram_file_size == 0: # Unknown size
        await message.reply_text(
            "File size is unknown. If it's very large, conversion might take a long time or fail."
        )


    processing_stop_event = asyncio.Event()
    feedback_task = asyncio.create_task(send_processing_feedback(context, update.effective_chat.id, processing_stop_event))

    try:
        tg_file = await context.bot.get_file(file_id)
        if not tg_file.file_path:
            await message.reply_text("Could not get file path from Telegram.")
            return

        file_download_url = tg_file.file_path # This is actually the relative path for bot's base_file_url

        await message.reply_text("Preparing to stream and convert... This might take a while for large files.")

        output_file_name = original_file_name.rsplit('.', 1)[0] + ".mp4"

        ffmpeg_cmd_copy = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", "pipe:0",  # Input from stdin
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            "-movflags", "frag_keyframe+empty_moov", # For streaming MP4
            "-f", "mp4",
            "pipe:1"  # Output to stdout
        ]

        ffmpeg_cmd_reencode = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", "pipe:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-strict", "experimental",
            "-movflags", "frag_keyframe+empty_moov",
            "-f", "mp4",
            "pipe:1"
        ]

        ffmpeg_process = None
        conversion_successful = False

        async def stream_download_to_ffmpeg(url, ffmpeg_stdin):
            try:
                async with httpx.AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            if chunk:
                                try:
                                    ffmpeg_stdin.write(chunk)
                                except BrokenPipeError:
                                    logger.warning("FFmpeg stdin pipe broken. Conversion might have ended or failed.")
                                    break
                        ffmpeg_stdin.close() # Signal EOF to ffmpeg
            except Exception as e:
                logger.error(f"Error during download/pipe to FFmpeg: {e}", exc_info=True)
                if hasattr(ffmpeg_stdin, 'close') and not ffmpeg_stdin.closed:
                     ffmpeg_stdin.close()


        for i, cmd in enumerate([ffmpeg_cmd_copy, ffmpeg_cmd_reencode]):
            if i == 1: # If first attempt (copy) failed
                await message.reply_text("Initial conversion (direct copy) failed or wasn't suitable. Attempting full re-encoding...")

            logger.info(f"Starting FFmpeg with command: {' '.join(cmd)}")
            ffmpeg_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Start streaming download to FFmpeg's stdin in a separate task
            # The file_path from get_file is relative, need to construct full URL
            full_download_url = f"{context.bot.base_file_url}{TELEGRAM_BOT_TOKEN}/{tg_file.file_path}"

            download_task = asyncio.create_task(stream_download_to_ffmpeg(full_download_url, ffmpeg_process.stdin))

            # At this point, ffmpeg_process.stdout is the stream of the converted MP4
            # We need to pass this stream to send_document
            # InputFile can take a file-like object. ffmpeg_process.stdout is an asyncio.StreamReader
            # We might need a wrapper if InputFile or send_document doesn't handle asyncio.StreamReader directly for streaming uploads.
            # For now, let's assume it can be handled or we'll read it into a BytesIO (though this defeats full streaming for upload)

            # Let's try sending the stdout StreamReader directly.
            # The filename is important for Telegram to display it correctly.
            # PTB's InputFile with read_file_handle=False might be the key for true streaming upload.
            # However, an asyncio.StreamReader is not a standard file handle.
            # We'll need an adapter or to read it into a buffer that PTB can handle.
            # For simplicity in this step, let's read stdout and then send. True output streaming is next.

            # Start streaming download to FFmpeg's stdin in a separate task
            full_download_url = f"{context.bot.base_file_url}{TELEGRAM_BOT_TOKEN}/{tg_file.file_path}"
            download_task = asyncio.create_task(stream_download_to_ffmpeg(full_download_url, ffmpeg_process.stdin))

            if ffmpeg_process.stdout is None:
                logger.error("FFmpeg stdout pipe is None. Cannot stream output.")
                await download_task
                if ffmpeg_process.stdin and not ffmpeg_process.stdin.is_closing():
                    ffmpeg_process.stdin.close() # pyright: ignore[reportUnknownMemberType]
                await ffmpeg_process.wait()
                await message.reply_text("Error: FFmpeg output stream could not be established.")
                continue

            await message.reply_text("Conversion processing... Uploading MP4 as it's being created...")

            # Async generator to feed `send_document`
            async def ffmpeg_output_stream_generator(stdout_pipe: asyncio.StreamReader):
                while True:
                    chunk = await stdout_pipe.read(1024 * 1024) # Read up to 1MB chunks
                    if not chunk:
                        break
                    yield chunk

            try:
                # The `document` parameter can take an asynchronous iterable of bytes.
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=ffmpeg_output_stream_generator(ffmpeg_process.stdout), # pyright: ignore[reportArgumentType]
                    filename=output_file_name,
                    # Timeouts might need adjustment for very large files / slow connections
                    # connect_timeout=20, read_timeout=60, write_timeout=300
                )
                # If send_document completes without error, we assume the upload was successful
                # Now we need to ensure FFmpeg also finished correctly.

                # Wait for download to finish feeding FFmpeg and FFmpeg to finish processing
                await download_task # Ensures stdin to FFmpeg is closed
                ffmpeg_return_code = await ffmpeg_process.wait() # Waits for FFmpeg to terminate

                ffmpeg_stderr_bytes = await ffmpeg_process.stderr.read() if ffmpeg_process.stderr else b'' # pyright: ignore[reportOptionalMemberAccess]
                ffmpeg_stderr = ffmpeg_stderr_bytes.decode().strip()

                if ffmpeg_return_code == 0:
                    logger.info(f"FFmpeg conversion and upload successful (attempt {i+1}). Stderr: {ffmpeg_stderr if ffmpeg_stderr else 'N/A'}")
                    await message.reply_text("MP4 file sent successfully!")
                    conversion_successful = True
                    break # Exit loop on success
                else:
                    # Upload might have appeared successful but FFmpeg had an error
                    logger.error(f"FFmpeg attempt {i+1} finished with error code {ffmpeg_return_code} after upload. Stderr: {ffmpeg_stderr}")
                    await message.reply_text(f"Conversion seemed to upload, but FFmpeg reported an error (code: {ffmpeg_return_code}). Error: {ffmpeg_stderr[:200]}")
                    # Decide if we should try the next command or not. If copy failed, re-encode might still work.
                    if i == 0: continue
                    return # Both attempts failed or this was the re-encode attempt

            except Exception as upload_err:
                logger.error(f"Error during streaming upload or FFmpeg processing for attempt {i+1}: {upload_err}", exc_info=True)
                await message.reply_text(f"Error during upload/conversion: {str(upload_err)[:200]}")
                # Ensure ffmpeg process is terminated if upload fails mid-stream
                if ffmpeg_process.returncode is None:
                    ffmpeg_process.kill()
                    await ffmpeg_process.wait()
                await download_task # ensure download task is also awaited
                if i == 0: continue # Try re-encoding
                return # Both attempts failed

        if not conversion_successful:
             await message.reply_text("Sorry, the conversion failed after all attempts.")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during download initiation: {e}", exc_info=True)
        await message.reply_text(f"Failed to download the file from Telegram: {e.response.status_code} {e.response.reason_phrase}")
    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        await message.reply_text(f"An error occurred: {str(e)[:1000]}")
    finally:
        processing_stop_event.set()
        await feedback_task # Ensure feedback task finishes

        # Clean up any subprocess if it's still running (shouldn't be if communicate() was awaited)
        if ffmpeg_process and ffmpeg_process.returncode is None:
            try:
                ffmpeg_process.kill()
                await ffmpeg_process.wait()
            except Exception as e_kill:
                logger.error(f"Error killing ffmpeg process: {e_kill}")
        logger.info("Cleaned up temporary files and FFmpeg process if any.")


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
