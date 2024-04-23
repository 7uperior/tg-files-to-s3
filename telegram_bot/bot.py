import os

from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

app = Client('Test1', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Mock database for user credits
user_credits = {}


# Define the custom audio filter
def audio_filter(_, __, message):
	if message.audio or (message.document and 'audio' in message.document.mime_type):
		return True
	return False


# Create the filter using filters.create
audio_filter = filters.create(audio_filter)


@app.on_message(audio_filter)
async def handle_audio(client, message):
	user_id = message.from_user.id
	duration = None

	# Check if it's an explicit audio message
	if message.audio:
		duration = message.audio.duration
	# Check if it's a document classified as audio
	elif message.document and 'audio' in message.document.mime_type:
		duration = message.document.duration

	# Initialize user's credits if not set
	if user_id not in user_credits:
		user_credits[user_id] = 100  # Initial credit

	# If duration is found, handle it
	if duration is not None:
		new_credits = user_credits[user_id] - duration

		if new_credits >= 0:
			user_credits[user_id] = new_credits
			await message.reply(f'Duration: {duration} seconds. Remaining credits: {new_credits} seconds.')
		else:
			await message.reply('You do not have enough credits on your balance for the bot to work.')


app.run()
