from pyrogram import Client, filters, errors
import logging
import os
import requests
from io import BytesIO
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

app = Client('tg_bot', in_memory=True, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

BASE_URL = "http://api:8000"
BALANCE_ENDPOINT = "/users/balance/"

@app.on_message(filters.regex(r"^/balance_(\d+)$") & filters.private)
async def receive_balance(client, message):
    client_id = message.matches[0].group(1)
    try:
        response = requests.get(f"{BASE_URL}{BALANCE_ENDPOINT}{client_id}")
        if response.ok:
            balance = response.json().get('balance')
            await message.reply(f"Balance for client {client_id}: {balance}")
        else:
            await message.reply(f"Failed to fetch balance: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        await message.reply(f"Network error occurred: {str(e)}")


@app.on_message((filters.audio | filters.voice) & filters.private)
async def audio_message_handler(client, message):
    try:
        # Check if the message is a voice message and handle accordingly
        is_voice = message.voice is not None
        mime_type = "audio/ogg" if is_voice else message.audio.mime_type
        
        # Determine file name and extension
        default_name = "voice_note" if is_voice else message.audio.file_name
        file_extension = "ogg" if is_voice else message.audio.file_name.split('.')[-1]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{default_name}_{message.from_user.id}_{timestamp}.{file_extension}"

        # Download the file to a temporary location
        raw_audio = await client.download_media(message)

        # Open the file and prepare it for sending using multipart/form-data
        with open(raw_audio, 'rb') as file:
            files = {'file': (file_name, file, mime_type)}
            response = requests.post(f"{BASE_URL}/files/", files=files)

            if response.ok:
                await message.reply("Audio file uploaded successfully!")
            else:
                # Parse the JSON response for specific error details and relay it back to the user
                error_details = response.json().get('detail', 'Failed to upload file.')
                await message.reply(f"Failed to upload file: {response.status_code} - {error_details}")
    except errors.FloodWait as e:
        logger.error(f"FloodWait: Have to wait for {e.x} seconds")
        await message.reply(f"Have to wait for {e.x} seconds before proceeding")
    except Exception as e:
        logger.exception("Failed to process audio message")
        await message.reply(f"An error occurred: {str(e)}")
    finally:
        if raw_audio and os.path.exists(raw_audio):
            os.remove(raw_audio)  # Clean up the file from local storage after upload

@app.on_message(filters.text & filters.private & ~filters.command(["balance_"]))
async def echo_message(client, message):
    await message.reply_text(f"You said: {message.text}")

if __name__ == "__main__":
    app.run()