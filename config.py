import os
import logging
from dotenv import load_dotenv

# Explicitly load .env from the current directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback to default

def get_int(key, default="0"):
    val = os.environ.get(key, default)
    if not val:
        return int(default)
    try:
        return int(val)
    except ValueError:
        return int(default)

# --- Required Variables --- #
API_HASH = os.environ.get("API_HASH", "")
APP_ID = get_int("APP_ID")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# Support both DB_URI and DATABASE_URL
DB_URI = os.environ.get("DB_URI") or os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DB_NAME") or os.environ.get("DATABASE_NAME", "BotDB")

OWNER_ID = get_int("OWNER_ID")
CHANNEL_ID = get_int("CHANNEL_ID")

# --- Optional Variables --- #
PORT = get_int("PORT", "8080")
TG_BOT_WORKERS = get_int("TG_BOT_WORKERS", "4")

# --- Pics and Videos --- #
PICS_STR = os.environ.get("PICS") or "https://telegra.ph/file/5593d624d11d92bceb48e.jpg"
PICS = PICS_STR.split()

START_PIC = os.environ.get("START_PIC") or PICS[0]
FORCE_PIC = os.environ.get("FORCE_PIC") or "https://telegra.ph/file/0d9e590f62b63b51d4bf9.jpg"
QR_PIC = os.environ.get("QR_PIC") or PICS[0]
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
START_MSG = os.environ.get('START_MESSAGE', 'Hello {mention}\n\nI can Download terabox files and having Advanced features 😎 .')
FORCE_MSG = os.environ.get('FORCE_SUB_MESSAGE', 'Hello {mention}\n\n<b>You need to join in my Channel/Group to use me\n\nKindly Please join Channel...\n\n❗Fᴀᴄɪɴɢ ᴘʀᴏʙʟᴇᴍs, ᴜsᴇ: /help</b>')
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

# --- Essential Validation --- #
missing = []
if not API_HASH: missing.append("API_HASH")
if not APP_ID: missing.append("APP_ID")
if not TG_BOT_TOKEN: missing.append("TG_BOT_TOKEN")
if not DB_URI: missing.append("DB_URI / DATABASE_URL")

if missing:
    logging.critical(f"Missing essential configuration: {', '.join(missing)}")
    logging.critical("Please set these in your environment or .env file.")
    logging.critical("Refer to sample.env or app.json for required variables.")
