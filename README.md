# MKV to MP4 Telegram Bot

This Telegram bot converts MKV video files to MP4 format.

## Features

- Responds to `/start` and `/help` commands.
- Handles MKV file uploads (sent as video or document).
- Converts MKV files to MP4 using FFmpeg, **now with streaming for better large file handling**.
  - Downloads the MKV file chunk by chunk and pipes it directly to FFmpeg's input.
  - FFmpeg's output (MP4) is streamed directly to Telegram for upload.
  - This significantly reduces disk space and memory usage compared to downloading/saving the entire file before processing.
  - Attempts to copy video/audio streams directly for speed (`-c:v copy -c:a aac`).
  - Falls back to full re-encoding (H.264 video, AAC audio: `-c:v libx264 -c:a aac`) if direct copy fails or is unsuitable.
- Sends the converted MP4 file back to the user.
- Provides periodic "typing..." feedback during processing.
- Informs users if a file is very large (e.g., >1GB), warning about potential long processing times or limits.
- No longer creates a `temp` directory for intermediate files, as processing is now in-memory/stream-based.

## Prerequisites

- Python 3.8+
- FFmpeg installed and available in your system's PATH.
- A Telegram Bot Token.

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Install FFmpeg:**
    *   **On Debian/Ubuntu:**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```
    *   **On macOS (using Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    *   **On Windows:**
        Download FFmpeg from [the official website](https://ffmpeg.org/download.html) and add the `bin` directory (containing `ffmpeg.exe`) to your system's PATH environment variable.

3.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up your Telegram Bot Token:**
    *   Talk to [BotFather](https://t.me/BotFather) on Telegram to create a new bot or get the token for an existing one.
    *   Set the token as an environment variable named `TELEGRAM_BOT_TOKEN`:
        ```bash
        export TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_BOT_TOKEN"
        ```
        (On Windows, use `set TELEGRAM_BOT_TOKEN=YOUR_ACTUAL_BOT_TOKEN` in Command Prompt or `$env:TELEGRAM_BOT_TOKEN="YOUR_ACTUAL_BOT_TOKEN"` in PowerShell).
        For persistent storage, you might want to add this to your shell's profile file (e.g., `.bashrc`, `.zshrc`) or use a `.env` file with a library like `python-dotenv` (though this is not implemented in the current `bot.py`).

## Running the Bot

Once you have completed the setup, run the bot using:

```bash
python bot.py
```

The bot will start polling for updates from Telegram.

## Usage

1.  Open a chat with your bot on Telegram.
2.  Send the `/start` command to see the welcome message.
3.  Send an MKV video file to the chat (either as a direct video upload or as a document).
4.  The bot will download the file, convert it, and send back the MP4 version.

## Project Structure

```
.
├── bot.py              # Main Python script for the Telegram bot
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Troubleshooting

*   **"TELEGRAM_BOT_TOKEN environment variable not set!"**: Make sure you have correctly set the `TELEGRAM_BOT_TOKEN` environment variable before running the bot.
*   **Conversion fails / FFmpeg errors**:
    *   Ensure FFmpeg is installed correctly and accessible from the command line (try running `ffmpeg -version`).
    *   The bot logs FFmpeg errors to the console. Check these logs for more details.
    *   Some MKV files might have unusual codecs or configurations that FFmpeg struggles with.
*   **Bot doesn't respond**:
    *   Check that the bot is running and that the `TELEGRAM_BOT_TOKEN` is correct.
    *   Look for any error messages in the console where the bot is running.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or find bugs.
