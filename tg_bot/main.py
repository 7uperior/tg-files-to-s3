from pyrogram import Client, filters
import logging
import os
import requests

logging.basicConfig(level=logging.INFO)

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

app = Client('tg_bot', in_memory=True, api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

# Define the base URL for your FastAPI service
BASE_URL = "http://api:8000"

# Define the endpoint for checking balance
BALANCE_ENDPOINT = "/users/balance/"

@app.on_message(filters.regex(r"^/balance_(\d+)$") & filters.private)
async def receive_balance(client, message):
    client_id = message.matches[0].group(1)
    try:
        # Send a GET request to the FastAPI service to get the balance
        response = requests.get(f"{BASE_URL}{BALANCE_ENDPOINT}{client_id}")
        if response.ok:
            balance = response.json().get('balance')
            await message.reply(f"Balance for client {client_id}: {balance}")
        else:
            await message.reply(f"Failed to fetch balance: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        await message.reply(f"Network error occurred: {str(e)}")

@app.on_message(filters.text & filters.private & ~filters.command(["balance_"]))
async def echo_message(client, message):
    # Echoes back the received message
    await message.reply_text(f"You said: {message.text}")

if __name__ == "__main__":
    # Start the bot
    app.run()
