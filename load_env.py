import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set default values if not found
if not os.getenv('TELEGRAM_BOT_TOKEN'):
    print("⚠️ TELEGRAM_BOT_TOKEN not set. Please set it in .env file")
    
if not os.getenv('ADMIN_BOT_TOKEN'):
    print("⚠️ ADMIN_BOT_TOKEN not set. Please set it in .env file")
    
if not os.getenv('ADMIN_PASSWORD'):
    print("⚠️ ADMIN_PASSWORD not set. Using default: admin123") 