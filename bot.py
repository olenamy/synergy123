import logging
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv
from aiogram import types
# from flask import Flask, request, jsonify

# app = Flask(__name__)
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# app = Flask(__name__)

# Load environment variables from .env
logger.debug("Loading environment variables from .env file.")
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
print("Bot token:", BOT_TOKEN)
USER_ID = os.getenv('USER_ID')

# Log the loaded variables
logger.debug(f"BOT_TOKEN loaded: {BOT_TOKEN is not None}")
logger.debug(f"USER_ID loaded: {USER_ID}")

# Check if the token was not loaded
if BOT_TOKEN is None:
    logger.error("BOT_TOKEN not loaded from .env file!")
    raise ValueError("BOT_TOKEN not loaded. Ensure your .env file is present.")

# Automatically detect the environment
# def detect_environment():
#     environment = "ngrok"  # Default to ngrok if hostname is not detected
#     # if "fly" in os.getenv('HOSTNAME', ''):
#     #     environment = "fly.io"
#     # elif "ngrok" in os.getenv('HOME', ''):
#     #     environment = "ngrok"

#     logger.debug(f"Environment detected: {environment}")
#     return environment

# Automatically set the webhook URL based on environment
def set_webhook_url():
    # environment = detect_environment()
    # if environment == "fly.io":
    #     return "https://mybot-divine-paper-6407.fly.dev/webhook"
    # else:
    # return os.getenv("WEBHOOK_URL") or "https://c982-2601-283-5081-5d50-48b7-11f6-a4cd-89ba.ngrok-free.app/webhook"
    return "https://synergy-3634.fly.dev/webhook"  # Default to Fly.io webhook URL
    
# Get webhook URL dynamically based on environment
WEBHOOK_URL = set_webhook_url()

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store user states
user_start_clicked = set()
users_with_initial_messages_sent = set()

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Timezone for Mountain Time (MT)
MT_TIMEZONE = pytz.timezone('America/Denver')

# Function to send scheduled message
async def send_scheduled_message(user_id, message_text):
    try:
        logger.debug(f"Sending scheduled message to {user_id}: {message_text}")
        await bot.send_message(user_id, message_text)
    except Exception as e:
        logger.error(f"Error sending scheduled message: {e}")

# @app.route("/webhook", methods=["POST"])
# async def handle_webhook(request):
#     logging.debug("Webhook hit")
#     try:
#         data = await request.json()
#         logging.debug(f"Webhook data received: {data}")
#         # Handle the incoming request
#     except Exception as e:
#         logging.error(f"Error processing webhook: {e}")
def handle_webhook():
    data = request.json
    logging.debug(f"Received webhook data: {data}")
    # Process the data here (e.g., sending a message to Telegram)
    return jsonify({'status': 'ok'}), 200

# Webhook handler for Fly.io
async def handle(request):
    # Handle incoming requests to the webhook endpoint
    # return web.Response(text="OK")
    try:
        update = await request.json()
        logger.debug(f"Received update: {update}")
        update_obj = Update(**update)

        # Feed the update to the dispatcher
        await dp.feed_update(update_obj)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return web.Response(status=200)  # Send a success status even if error occurred

# Start webhook server for Fly.io
async def start_server():
    # Create the aiohttp web application and add the routes
    app = web.Application()
    app.add_routes([web.post('/webhook', handle)])

    # Run the aiohttp app without blocking the current event loop
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    logger.debug("Webhook server running...")
    
# Delete any existing webhook
async def delete_webhook():
    """Delete any existing webhook before starting polling or setting a new webhook."""
    webhook_response = await bot.delete_webhook()
    logger.debug(f"Webhook deleted: {webhook_response}")

# Set the webhook URL (for production)
# async def set_webhook():
#     # Simulate setting the webhook
#     logger.debug("Setting webhook...")
#     # Add logic to actually set the webhook if needed
#     # response = await some_webhook_function()
#     return True
async def set_webhook():
    try:
        webhook_url = set_webhook_url()  # Get your URL dynamically
        logger.debug(f"Setting webhook URL: {webhook_url}")
        
        # Set webhook
        webhook_response = await bot.set_webhook(webhook_url)
        logger.debug(f"Webhook set response: {webhook_response}")
        
        # Verify webhook status
        webhook_info = await bot.get_webhook_info()
        logger.debug(f"Webhook info: {webhook_info}")
        
        return True
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return False


async def check_webhook_status():
    webhook_info = await bot.get_webhook_info()
    logger.debug(f"Webhook info: {webhook_info}")

# Handle /start command
@dp.message(CommandStart())
async def start(message: types.Message):
    logger.debug(f"Received /start from {message.from_user.id}")
    try:
        user_id = message.from_user.id

        # # Check if this is the first time the user has clicked /start
        # if user_id not in user_start_clicked:
        #     user_start_clicked.add(user_id)
        #     logger.debug(f"Sending welcome messages to {user_id}")

            # Welcome message
        await message.answer(
            text=f"Hello, <b>{message.from_user.full_name}!</b> Welcome to New Year 2025 Compass Workshop!",
            parse_mode='HTML'
        )

        # Social media buttons
        instagram_button = types.InlineKeyboardButton(
            text="Follow me on Instagram", 
            url="https://www.instagram.com/olenka_myronenko/"
        )
        tiktok_button = types.InlineKeyboardButton(
            text="Follow me on TikTok", 
            url="https://www.tiktok.com/@olenanumerology"
        )
        website_button = types.InlineKeyboardButton(
            text="My Website", 
            url="https://numerologysynergy.com/"
        )
        social_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [instagram_button],
            [tiktok_button],
            [website_button]
        ])

        await message.answer(
            "It's me Olena Myronenko. I am so excited to start this journey of new fulfilled life with you in 2025.",
            reply_markup=social_keyboard
        )
        await asyncio.sleep(5)

            # More messages to follow (as per your existing logic)

        await message.answer(
            text="""<b><u>What to Expect?</u></b>

✔️ <b>You have gained access to telegram bot already and that's where all the workshop going to be happening.</b>
Pay attention below bot will send you your 1st valuable lesson to watch right now down below.

✔️ <b>Every day for the next 3 days at 9am MT you will be receiving all the valuable lessons and materials.</b>
The reason is for you to get the most knowledge for yourself and pump up your motivation. 

✔️ <b>Additionally at the end you will get practices specifically for you to make your year 2025 more magical.</b>
Practices specifically designed for you to implement throughout the whole year to make you feel you can get what you need in 2025. 

✔️ <b>You are gaining access to this workshop for a year!</b>
You can come back any time and refresh your memory, use it as a valuable resource and review it again when you need it the most.

<i>All the knowledge you will receive during the workshop check out next ⬇️</i>""",
                parse_mode='HTML'
            )
        await asyncio.sleep(10)

        await message.answer(
            text="""<b>Here is what you will learn:</b>

🔥 How to manifest your desires and goals for 2025.

🔥 Powerful techniques to improve your mindset and motivation.

🔥 How to break old patterns and create new empowering habits.

🔥 How to align with your true purpose to achieve your dreams.

🔥 And much more to make 2025 your most magical year yet!""",
                parse_mode='HTML'
            )

        await asyncio.sleep(5)
    
    except Exception as e:
        # Log the error (this part should still catch errors if any occur)
        logger.exception("Exception details")
           
        await message.answer("Let's get started. You are getting your day 1 lesson right now! 🎓")
            
        await asyncio.sleep(5)
        
        video_url = "https://youtu.be/6F99NcfJPAc"
        thumbnail_url = "https://drive.google.com/uc?id=1Pk0v5eOhF78j_sgO1LoIVVGkZK5BDKrJ&export=download"

        video_button = types.InlineKeyboardButton(text="▶️ Watch Day 1 Lesson", url=video_url)
        more_info_button = types.InlineKeyboardButton(text="ℹ️ Learn More", url="https://numerologysynergy.com/") 
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[video_button], [more_info_button]])
        # Wrap the code with try-except for error handling
        try:
            # Send the photo with the thumbnail and caption, with an inline keyboard attached
            await message.answer_photo(
                caption="<b>Day 1 Video Lesson 🚀 </b>\n\n"
                        "<i>Click below to start your learning journey! ✨ </i>",
                photo=thumbnail_url,        
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except Exception as e:
            # Log the error
            logger.error(f"Failed to send video or thumbnail for user {message.from_user.id}: {e}")
    
            # Send a user-friendly error message
            await message.answer(
                "Oops! Something went wrong while trying to send your video lesson. Please try again later or contact support."
            )

        await asyncio.sleep(5)
        
        await message.answer(
                text=f"<b>{message.from_user.first_name}! The remaining lessons you will be receiving every day for next 3 days by 12pm MT ⏳ </b>",
                parse_mode='HTML'
            )
                
        users_with_initial_messages_sent.add(user_id)

        # More scheduler setup logic here...

    # except Exception as e:
    #     logger.error(f"Error in /start command: {e}")

            # Get current time in MT timezone
        now = datetime.now(MT_TIMEZONE)
        logger.debug(f"Scheduling messages at: {now}")

        # Schedule messages for the user after the first greeting
        scheduler.add_job(send_scheduled_message, 'date', run_date=now + timedelta(minutes=3), args=[user_id, "Hi, it's message 1 in the scheduler"])
        scheduler.add_job(send_scheduled_message, 'date', run_date=now.replace(hour=23, minute=30, second=0, microsecond=0), args=[user_id, "Hi, it's message 2 in the scheduler"])

        # 3. Third, Fourth, and Fifth messages: Send starting tomorrow at 12:01 AM MT and repeat every day
        start_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        scheduler.add_job(send_scheduled_message, 'date', run_date=start_date, args=[user_id, "Hi, it's message 3 in the scheduler"])
        logger.debug(f"Scheduling message 3 for: {start_date}")
        scheduler.add_job(send_scheduled_message, 'date', run_date=start_date + timedelta(days=1), args=[user_id, "Hi, it's message 4 in the scheduler"])
        logger.debug(f"Scheduling message 4 for: {start_date + timedelta(days=1)}")
        scheduler.add_job(send_scheduled_message, 'date', run_date=start_date + timedelta(days=2), args=[user_id, "Hi, it's message 5 in the scheduler"])
        logger.debug(f"Scheduling message 5 for: {start_date + timedelta(days=2)}")
        
        # Start the scheduler if it's not already running
        if not scheduler.running:
            scheduler.start()
        else:
            await message.answer("You have already started. Let me know if you need assistance!")

    except Exception as e:
        logger.error(f"Error in /start command: {e}")

# Handle other user messages
@dp.message()
async def handle_user_message(message: types.Message):
    try:
        user_id = message.from_user.id

        if user_id in users_with_initial_messages_sent:
            await message.answer(
                "This bot is only used to deliver valuable workshop information. If you have any technical difficulties, please reach out to olenam.numerology@gmail.com and we will be in touch."
            )
    except Exception as e:
        logger.error(f"Error in handle_user_message: {e}")

# Main entry point to start the bot
async def main():
    try:
        # Clear the user start interaction state before starting the bot
        user_start_clicked.clear()  # This will reset the users who have interacted with the /start command
        logger.debug("Bot is starting...")
        
        await set_webhook()
        # if "ngrok" in WEBHOOK_URL:  # Use polling when running locally
        #     # Delete any existing webhook before starting polling
        #     await delete_webhook()
        #     # Start polling for local development (ngrok)
        #     await dp.start_polling(bot)  # This line should only be used for local polling with ngrok
        await asyncio.create_task(start_server())

        logger.debug("Bot is running... Press Ctrl+C to stop.")

        # The bot will continue running here, waiting for webhook requests to come in.
        # We keep the event loop alive, so the bot will keep running indefinitely.
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour to keep the event loop running
        
        #  # Start the webhook server for production (Fly.io)
        # # logger.debug("Starting server with webhook: %s", WEBHOOK_URL)
        # app = web.Application()
        # app.add_routes([web.post('/webhook', handle)])  # Add the webhook handler
        # # await web.run_app(app, host='0.0.0.0', port=8080)  # Run the aiohttp app in the existing event loop

        # # Run the aiohttp server in the background using asyncio.create_task()
        # server_task = asyncio.create_task(web.run_app(app, host='0.0.0.0', port=8080))

        # logger.debug("Bot is running... Press Ctrl+C to stop.")

        # # Start the webhook server for production (in background)
        # asyncio.create_task(start_server())  # Run in the background

        # logger.debug("Bot is running... Press Ctrl+C to stop.")
        # while True:
        #     await asyncio.sleep(3600)  # Keep the bot running

        # Keep the main function running while the server is serving requests
        # await server_task
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)
#     try:
#         # Ensure we only have one event loop running
#         if not asyncio.get_event_loop().is_running():
#             asyncio.run(main())  # Start the main function if no event loop is running
#         else:
#             loop = asyncio.get_event_loop()
#             loop.create_task(main())  # Use the existing event loop to run the main function

#     except KeyboardInterrupt:
#         logger.info("Bot stopped by user.")
#     except Exception as e:
#         logger.error(f"Unexpected error occurred: {e}")
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")

# # Start polling to fetch updates
# executor.start_polling(dp, skip_updates=True)

