# # from flask import Flask, request

# # app = Flask(__name__)

# # # Define a route for the root
# # @app.route('/')
# # def home():
# #     return 'Welcome to the home page!'

# # # Define a route for the favicon
# # @app.route('/favicon.ico')
# # def favicon():
# #     return '', 204  # Respond with no content

# # # Your existing webhook route
# # @app.route('/webhook', methods=['POST'])
# # def webhook():
# #     print(request.json)  # Log the incoming data from Telegram
# #     return 'OK'

# # if __name__ == '__main__':
# #     app.run(debug=True, host='0.0.0.0', port=8082)


# import aiohttp.web

# # Define your app and routes here
# app = aiohttp.web.Application()

# # Route for root
# async def root(request):
#     return aiohttp.web.Response(text="Welcome to the root!")

# # Route for favicon.ico
# async def favicon(request):
#     return aiohttp.web.Response(status=204)  # No content response

# # Your webhook route
# async def webhook(request):
#     data = await request.json()
#     print(data)  # Log the incoming data from Telegram
#     return aiohttp.web.Response(text='OK')

# # Add routes to the app
# app.router.add_get('/', root)
# app.router.add_get('/favicon.ico', favicon)
# app.router.add_post('/webhook', webhook)

# # Run the app
# if __name__ == '__main__':
#     aiohttp.web.run_app(app, host='0.0.0.0', port=8083)

import logging
import os
import asyncio
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

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

# Log the loaded variables
logger.debug(f"BOT_TOKEN loaded: {BOT_TOKEN is not None}")
logger.debug(f"USER_ID loaded: {USER_ID}")

# Check if the token is loaded
if BOT_TOKEN is None:
    logger.error("BOT_TOKEN not loaded from .env file!")
    raise ValueError("BOT_TOKEN not loaded. Ensure your .env file is present.")

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

# Webhook handler for Fly.io
async def handle(request):
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

    # Define routes for root and favicon
    async def root(request):
        return web.Response(text="Welcome to the root!")

    async def favicon(request):
        return web.Response(status=204)  # No content response

    app.add_routes([web.get('/', root)])
    app.add_routes([web.get('/favicon.ico', favicon)])

    # Add the webhook route
    app.add_routes([web.post('/webhook', handle)])

    # Run the aiohttp app without blocking the current event loop
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8084)
    await site.start()

    logger.debug("Webhook server running...")

# Set webhook dynamically based on environment
async def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL', 'https://synergy-3634.fly.dev/webhook')  # Default to Fly.io webhook URL
    logger.debug(f"Setting webhook URL: {webhook_url}")

    # Set webhook
    webhook_response = await bot.set_webhook(webhook_url)
    logger.debug(f"Webhook set response: {webhook_response}")

    # Verify webhook status
    webhook_info = await bot.get_webhook_info()
    logger.debug(f"Webhook info: {webhook_info}")

    return True

# Delete existing webhook if necessary
async def delete_webhook():
    try:
        webhook_response = await bot.delete_webhook()
        logger.debug(f"Webhook deleted: {webhook_response}")
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")

# Handle /start command
@dp.message(CommandStart())
async def start(message: types.Message):
    logger.debug(f"Received /start from {message.from_user.id}")
    try:
        user_id = message.from_user.id

        # Check if the user has already clicked /start
        if user_id in user_start_clicked:
            await message.answer("You have already started!")
            return

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

        # Send the first video lesson
        video_url = "https://youtu.be/6F99NcfJPAc"
        thumbnail_url = "https://drive.google.com/uc?id=1Pk0v5eOhF78j_sgO1LoIVVGkZK5BDKrJ&export=download"

        video_button = types.InlineKeyboardButton(text="▶️ Watch Day 1 Lesson", url=video_url)
        more_info_button = types.InlineKeyboardButton(text="ℹ️ Learn More", url="https://numerologysynergy.com/") 
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[video_button], [more_info_button]])

        await message.answer_photo(
            caption="<b>Day 1 Video Lesson 🚀 </b>\n\n"
                    "<i>Click below to start your learning journey! ✨ </i>",
            photo=thumbnail_url,        
            parse_mode='HTML',
            reply_markup=keyboard
        )

        await asyncio.sleep(5)
        
        await message.answer(
                text=f"<b>{message.from_user.first_name}! The remaining lessons you will be receiving every day for next 3 days by 12pm MT ⏳ </b>",
                parse_mode='HTML'
            )
                
        users_with_initial_messages_sent.add(user_id)

        # Get current time in MT timezone
        now = datetime.now(MT_TIMEZONE)
        logger.debug(f"Scheduling messages at: {now}")

        # Schedule messages for the user after the first greeting
        scheduler.add_job(send_scheduled_message, 'date', run_date=now + timedelta(minutes=3), args=[user_id, "Hi, it's message 1 in the scheduler"])
        scheduler.add_job(send_scheduled_message, 'date', run_date=now.replace(hour=23, minute=30, second=0, microsecond=0), args=[user_id, "Hi, it's message 2 in the scheduler"])

        # 3. Third, Fourth, and Fifth messages: Send starting tomorrow at 12:01 AM MT and repeat every day
        start_date = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        scheduler.add_job(send_scheduled_message, 'date', run_date=start_date, args=[user_id, "Hi, it's message 3 in the scheduler"])
        
    except Exception as e:
        logger.exception("Error in /start command")

# Main entry point to start the bot
async def main():
    try:
        # Start webhook server and bot
        await set_webhook()
        await start_server()  # Start the aiohttp server

        logger.debug("Bot is running... Press Ctrl+C to stop.")

        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour to keep the event loop running

    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
