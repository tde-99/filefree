import os
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Required Variables --- #
API_HASH = os.environ.get("API_HASH", "")
APP_ID = int(os.environ.get("APP_ID", "0"))
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "BotDB")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))

# --- Optional Variables --- #
PORT = int(os.environ.get("PORT", "8080"))
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

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
REFERRAL_COUNT = int(os.environ.get("REFERRAL_COUNT", "10"))
REFERRAL_PREMIUM_DAYS = int(os.environ.get("REFERRAL_PREMIUM_DAYS", "7"))

# --- Other Settings --- #
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>{file_name}</b>")
MIN_ID = int(os.environ.get("MIN_ID", "1"))
MAX_ID = int(os.environ.get("MAX_ID", "1000"))
VIDEOS_RANGE = range(MIN_ID, MAX_ID + 1)

# --- Logging --- #
logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger
