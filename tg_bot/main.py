from pyrogram import Client, filters, errors
import logging
import os
import requests
from io import BytesIO
import datetime
from math import floor

def round_down(value, decimals):
    factor = 10 ** decimals
    return floor(value * factor) / factor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

app = Client('tg_bot', in_memory=True, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

BASE_URL = "http://api:8000"
BALANCE_ENDPOINT = "/users/balance/"

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    telegram_id = str(message.from_user.id)
    try:
        # Create a new user with the Telegram ID
        response = requests.post(f"{BASE_URL}/users/create_via_tgid", json={'telegram_id': telegram_id})
        if response.ok:
            await message.reply("Welcome to the service! Your account has been created with 10 credits.")
        else:
            await message.reply(f"Failed to create user account: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        await message.reply(f"Network error occurred: {str(e)}")

@app.on_message(filters.command("balance") & filters.private)
async def receive_balance(client, message):
    telegram_id = str(message.from_user.id)
    try:
        # Assuming your backend handles Telegram ID as a unique identifier for fetching balance
        response = requests.get(f"{BASE_URL}{BALANCE_ENDPOINT}{telegram_id}")
        if response.ok:
            balance_response = response.json().get('balance')
            balance = round_down(balance_response,2)
            await message.reply(f"Your current balance is: {balance}", quote=True)
        else:
            await message.reply(f"Failed to fetch balance: {response.status_code} - {response.text}", quote=True)
    except requests.exceptions.RequestException as e:
        await message.reply(f"Network error occurred: {str(e)}", quote=True)


@app.on_message((filters.audio | filters.voice) & filters.private)
async def handle_file_upload(client, message):
    telegram_id = str(message.from_user.id)
    is_voice = message.voice is not None
    mime_type = "audio/ogg" if is_voice else message.audio.mime_type

    default_file_name = "voice_note" if is_voice else message.audio.file_name
    file_extension = "ogg" if is_voice else message.audio.file_name.split('.')[-1]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{default_file_name}_{message.from_user.id}_{timestamp}.{file_extension}"

    file_size = message.voice.file_size if is_voice else message.audio.file_size
    file_size_mb = file_size / (1024 * 1024)

    audio_duration = message.voice.duration if is_voice else message.audio.duration

    pricing_response = requests.get(f"{BASE_URL}/settings/filespricing/latest")
    if not pricing_response.ok:
        await message.reply("Failed to retrieve file pricing details.")
        return

    pricing = pricing_response.json()
    price_per_second = pricing.get('price_per_second', 0.01)
    estimated_cost = round(file_size_mb * pricing['price_per_size'] + audio_duration * price_per_second, 2)
    buffer_cost = round(estimated_cost * (1 + (pricing['extra_buffer_percentage'] / 100)), 2)

    balance_response = requests.get(f"{BASE_URL}{BALANCE_ENDPOINT}{telegram_id}")
    if not balance_response.ok:
        await message.reply("Failed to fetch your balance. Please try again later.")
        return

    balance_data = balance_response.json()
    balance = balance_data['balance']
    balance_rounded = round_down(balance, 2)

    if balance_rounded < buffer_cost:
        await message.reply(f"Insufficient balance to upload the file {default_file_name}. Please top up your account.", quote=True)
        return

    # Deduct the buffer-included cost from the user’s balance
    deduct_url = f"{BASE_URL}/users/transactions/reduction-tg-bot?telegram_id={telegram_id}&amount={buffer_cost}"
    deduct_response = requests.post(deduct_url)
    if not deduct_response.ok:
        await message.reply("Failed to deduct balance. Transaction aborted.")
        return

    # Download the file to a temporary location
    try:
        raw_audio = await client.download_media(message)

        # Open the file and prepare it for sending using multipart/form-data
        with open(raw_audio, 'rb') as file:
            files = {'file': (file_name, file, mime_type)}
            response = requests.post(f"{BASE_URL}/files/", files=files)

            if response.ok:
                await message.reply(f"Audio file {default_file_name} uploaded successfully to S3!")
            else:
                error_details = response.json().get('detail', 'Failed to upload file.')
                await message.reply(f"Failed to upload file: {response.status_code} - {error_details}")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
    finally:
        if raw_audio and os.path.exists(raw_audio):
            os.remove(raw_audio)  # Clean up the file from local storage after upload

@app.on_message(filters.text & filters.private & ~filters.command(["balance_"]))
async def echo_message(client, message):
    # Reply to the message
    await message.reply_text(f"You said: {message.text}", quote=True)
 

if __name__ == "__main__":
    app.run()


