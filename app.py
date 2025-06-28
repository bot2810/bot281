from flask import Flask, request
import telebot
from telebot import types
import re
import time
import uuid
import threading
import json
import os
from datetime import datetime, timedelta
import pytz
import logging
import random

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7929115529'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
SECRET_TOKEN = os.getenv('SECRET_TOKEN', str(uuid.uuid4()))

# Initialize bot
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    raise

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid content type', 403

# Health check route
@app.route('/')
def health_check():
    return 'Bot is running!', 200

# [PASTE ALL YOUR ORIGINAL BOT CODE HERE]
# Include all the functions, handlers, and logic from your original code
# from "✅ BOT USERNAME CACHE" to the end of the file

# Modified run_bot function for Render
def run_bot():
    logger.info("Starting bot in production mode...")
    
    # Configure webhook if URL is provided
    if WEBHOOK_URL:
        logger.info(f"Configuring webhook at {WEBHOOK_URL}/webhook")
        bot.remove_webhook()
        time.sleep(1)
        
        webhook_url = f"{WEBHOOK_URL}/webhook"
        bot.set_webhook(
            url=webhook_url,
            secret_token=SECRET_TOKEN
        )
        logger.info(f"Webhook configured successfully at {webhook_url}")
    else:
        logger.warning("WEBHOOK_URL not set, falling back to polling")
        bot.infinity_polling()

if __name__ == "__main__":
    # Start background threads
    try:
        save_thread = threading.Thread(target=auto_save, daemon=True)
        save_thread.start()
        logger.info("Auto-save thread started")
    except Exception as e:
        logger.error(f"Failed to start auto-save thread: {e}")

    try:
        emoji_thread = threading.Thread(target=emoji_rotation_monitor, daemon=True)
        emoji_thread.start()
        logger.info("Emoji rotation thread started")
    except Exception as e:
        logger.error(f"Failed to start emoji rotation thread: {e}")

    # Run the bot
    run_bot()
    
    # Start Flask app if in webhook mode
    if WEBHOOK_URL:
        port = int(os.environ.get('PORT', 10000))
        app.run(
            host='0.0.0.0',
            port=port,
            threaded=True
        )
