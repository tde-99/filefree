import os
import logging
from dotenv import load_dotenv

load_dotenv()

def get_int(key, default="0"):
    val = os.environ.get(key, default)
    if not val:
        return int(default)
    return int(val)

# --- Required Variables --- #
API_HASH = os.environ.get("API_HASH", "")
APP_ID = get_int("APP_ID")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "BotDB")
OWNER_ID = get_int("OWNER_ID")
CHANNEL_ID = get_int("CHANNEL_ID")

# --- Optional Variables --- #
PORT = get_int("PORT", "8080")
TG_BOT_WORKERS = get_int("TG_BOT_WORKERS", "4")

# --- Pics and Videos --- #
PICS = os.environ.get("PICS", "https://telegra.ph/file/5593d624d11d92bceb48e.jpg").split()
START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/5593d624d11d92bceb48e.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/0d9e590f62b63b51d4bf9.jpg")
QR_PIC = os.environ.get("QR_PIC", "https://telegra.ph/file/5593d624d11d92bceb48e.jpg")
TUT_VID = os.environ.get("TUT_VID", "")

# --- Pricing and UPI --- #
PRICE1 = os.environ.get("PRICE1", "50 INR")
PRICE2 = os.environ.get("PRICE2", "100 INR")
PRICE3 = os.environ.get("PRICE3", "250 INR")
PRICE4 = os.environ.get("PRICE4", "450 INR")
PRICE5 = os.environ.get("PRICE5", "800 INR")
UPI_ID = os.environ.get("UPI_ID", "")
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", "")

# --- Referral System --- #
REFERRAL_COUNT = get_int("REFERRAL_COUNT", "10")
REFERRAL_PREMIUM_DAYS = get_int("REFERRAL_PREMIUM_DAYS", "7")

# --- Other Settings --- #
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>{file_name}</b>")
MIN_ID = get_int("MIN_ID", "1")
MAX_ID = get_int("MAX_ID", "1000")
VIDEOS_RANGE = range(MIN_ID, MAX_ID + 1)

# --- Logging --- #
logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger

# --- Validation --- #
if not all([API_HASH, APP_ID, TG_BOT_TOKEN, DB_URI]):
    logging.warning("One or more essential environment variables are missing (API_HASH, APP_ID, TG_BOT_TOKEN, DB_URI). The bot may not start correctly.")
