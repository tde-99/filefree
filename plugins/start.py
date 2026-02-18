
import asyncio
import base64
import logging
import os
import random
import re
import string
import time

from datetime import datetime, timedelta
from pytz import timezone
import pytz

from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import (
    Message,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    InputMediaVideo,
    ReplyKeyboardMarkup,
)
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from plugins.autoDelete import auto_del_notification, delete_message
from bot import Bot
from config import *
from helper_func import *
from database.database import db
from database.db_premium import *
from plugins.FORMATS import *

# Logging + timezone
logging.basicConfig(level=logging.INFO)
IST = timezone("Asia/Kolkata")

async def get_btn_markup():
    """Helper to get channel buttons markup from DB"""
    try:
        if await db.get_channel_button():
            button_name, button_link, button_name2, button_link2 = await db.get_channel_button_links()
            buttons = []
            if button_name and button_link:
                buttons.append([InlineKeyboardButton(text=button_name, url=button_link)])
            if button_name2 and button_link2:
                if buttons:
                    buttons[0].append(InlineKeyboardButton(text=button_name2, url=button_link2))
                else:
                    buttons.append([InlineKeyboardButton(text=button_name2, url=button_link2)])
            if buttons:
                return InlineKeyboardMarkup(buttons)
    except Exception as e:
        logging.error(f"Error generating btn markup: {e}")
    return None


@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    user_id = id
    text = message.text or ""
    logging.info(f"Received /start command from user ID: {id}")

    # Check if user is banned
    if await db.ban_user_exist(user_id):
        return await message.reply_text(BAN_TXT, quote=True)

    # Check if user is subscribed
    if not await is_subscribed(client, message):
        return await not_joined(client, message)

    # Fetch verify status + expiry duration
    try:
        verify_status = await db.get_verify_status(id) or {}
        VERIFY_EXPIRE = await db.get_verified_time()
    except Exception as e:
        logging.error(f"Error fetching verify status/config: {e}")
        verify_status = {"is_verified": False}
        VERIFY_EXPIRE = None

    # Handle expired verification:
    if verify_status.get("is_verified") and VERIFY_EXPIRE:
        verified_time = verify_status.get("verified_time", 0)
        if (time.time() - verified_time) > VERIFY_EXPIRE:
            await db.update_verify_status(id, is_verified=False)
            verify_status["is_verified"] = False

    # Add user if not exists
    if not await db.present_user(id):
        await db.add_user(id)

    # Referral system handling
    if "ref_" in text:
        try:
            _, ref_user_id_str = text.split("_", 1)
            ref_user_id = int(ref_user_id_str)
            if ref_user_id and ref_user_id != user_id:
                if not await db.check_referral_exists(user_id):
                    if await db.add_referral(ref_user_id, user_id):
                        referral_count = await db.get_referral_count(ref_user_id)
                        if REFERRAL_COUNT and referral_count > 0 and (referral_count % REFERRAL_COUNT == 0):
                            await add_premium(ref_user_id, REFERRAL_PREMIUM_DAYS, "d")
                            try:
                                await client.send_message(ref_user_id, f"🎉 Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! Yᴏᴜ'ᴠᴇ ʀᴇᴄᴇɪᴠᴇᴅ {REFERRAL_PREMIUM_DAYS} ᴅᴀʏs ᴏғ Pʀᴇᴍɪᴜᴍ!")
                            except: pass
        except: pass

    # Token verification flow
    if "verify_" in text:
        try:
            _, token = text.split("_", 1)
            if token and verify_status.get("verify_token") == token:
                await db.update_verify_status(user_id, is_verified=True, verified_time=time.time())
                expiry_text = get_exp_time(VERIFY_EXPIRE) if VERIFY_EXPIRE else "the configured duration"
                return await message.reply(f"✅ Token Verified Successfully!\n\n🔑 Valid For: {expiry_text}.", quote=True)
            else:
                return await message.reply("⚠️ Invalid/Expired Token. Use /start again.")
        except: pass

    # Handle get_again triggers
    for action in ["photo", "video", "batch"]:
        if text.startswith(f"get_{action}_"):
            try:
                _, user_id_str = text.split("_", 2)
                if int(user_id_str) == user_id:
                    if action == "photo": return await get_photo(client, message)
                    if action == "video": return await get_video(client, message)
                    if action == "batch": return await get_batch(client, message)
            except: pass

    # Welcome message with keyboard
    reply_kb = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Get Photo 📸"), KeyboardButton("Get Batch 📦")],
            [KeyboardButton("Get Video 🍒"), KeyboardButton("Plan Status 🔖")],
        ],
        resize_keyboard=True,
    )

    referral_link = f"https://telegram.dog/{client.username}?start=ref_{user_id}"
    start_msg_db = await db.get_start_msg()
    caption = (start_msg_db or START_MSG).format(
        mention=message.from_user.mention,
        id=message.from_user.id,
    ) + f"\n\n🎁 <b>Referral System:</b>\n🔗 Your Link: <code>{referral_link}</code>\n📊 Refer {REFERRAL_COUNT} users = {REFERRAL_PREMIUM_DAYS} Days Premium!"

    try:
        await message.reply_photo(photo=START_PIC, caption=caption, reply_markup=reply_kb)
    except:
        await message.reply(caption, reply_markup=reply_kb)

@Bot.on_message(filters.command('check') & filters.private)
async def check_command(client: Client, message: Message):
    user_id = message.from_user.id
    if await is_premium_user(user_id):
        return await message.reply_text("✅ Yᴏᴜ ᴀʀᴇ ᴀ Pʀᴇᴍɪᴜᴍ Usᴇʀ.\n\n🔓 Nᴏ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɴᴇᴇᴅᴇᴅ!", quote=True)

    verify_status = await db.get_verify_status(user_id) or {}
    VERIFY_EXPIRE = await db.get_verified_time()

    if verify_status.get("is_verified", False):
        expiry_text = get_exp_time(VERIFY_EXPIRE) if VERIFY_EXPIRE else "the configured duration"
        return await message.reply_text(f"✅ Yᴏᴜ ᴀʀᴇ ᴠᴇʀɪғɪᴇᴅ.\n\n🔑 Vᴀʟɪᴅ ғᴏʀ: {expiry_text}.", quote=True)

    shortener_url = await db.get_shortener_url()
    shortener_api = await db.get_shortener_api()

    if shortener_url and shortener_api:
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        await db.update_verify_status(user_id, verify_token=token)
        long_url = f"https://telegram.dog/{client.username}?start=verify_{token}"
        short_link = await get_shortlink(long_url)
        tut_vid_url = await db.get_tut_video() or TUT_VID

        btn = [[InlineKeyboardButton("Click here", url=short_link), InlineKeyboardButton('How to use', url=tut_vid_url)], [InlineKeyboardButton('BUY PREMIUM', callback_data='buy_prem')]]
        expiry_text = get_exp_time(VERIFY_EXPIRE) if VERIFY_EXPIRE else "the configured duration"
        await message.reply(f"Your ads token is expired. Verify to access files.\n\nToken Timeout: {expiry_text}", reply_markup=InlineKeyboardMarkup(btn), quote=True)
    else:
        await message.reply_text("⚠️ Verification needed. Use /start.", quote=True)

@Bot.on_message(filters.regex("Plan Status 🔖"))
async def on_plan_status(client: Client, message: Message):
    user_id = message.from_user.id
    if await db.ban_user_exist(user_id): return await message.reply_text(BAN_TXT, quote=True)
    if not await is_subscribed(client, message): return await not_joined(client, message)

    is_premium = await is_premium_user(user_id)
    free_limit = await db.get_free_limit(user_id)
    free_enabled = await db.get_free_state(user_id)
    free_count = await db.check_free_usage(user_id)

    if is_premium:
        user_data = await db.collection.find_one({"user_id": user_id})
        exp = user_data.get("expiration_timestamp")
        if exp:
            remaining = datetime.fromisoformat(exp).astimezone(IST) - datetime.now(IST)
            expiry_info = f"{remaining.days}d {remaining.seconds // 3600}h {(remaining.seconds // 60) % 60}m {remaining.seconds % 60}s left"
            status = f"Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴛᴀᴛᴜs: Pʀᴇᴍɪᴜᴍ ✅\n\nRᴇᴍᴀɪɴɪɴɢ Tɪᴍᴇ: {expiry_info}\n\nVɪᴅᴇᴏs Rᴇᴍᴀɪɴɪɴɢ Tᴏᴅᴀʏ: Uɴʟɪᴍɪᴛᴇᴅ 🎉"
        else:
            status = "Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴛᴀᴛᴜs: Pʀᴇᴍɪᴜᴍ ✅\n\nPʟᴀɴ Exᴘɪʀʏ: N/A"
        await message.reply_text(status, reply_markup=ReplyKeyboardMarkup([["Plan Status 🔖", "Get Video 🍒"]], resize_keyboard=True), quote=True)
    elif free_enabled:
        status = f"Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴛᴀᴛᴜs: Fʀᴇᴇ 🆓\n\nVɪᴅᴇᴏs Rᴇᴍᴀɪɴɪɴɢ Tᴏᴅᴀʏ: {free_limit - free_count}/{free_limit}"
        await message.reply_text(status, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")]]), quote=True)
    else:
        await message.reply_text("Free plan disabled.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", callback_data="buy_prem")]]), quote=True)

@Bot.on_message(filters.regex("Get Video 🍒"))
async def on_get_video(client: Client, message: Message):
    if await db.ban_user_exist(message.from_user.id): return await message.reply_text(BAN_TXT, quote=True)
    if not await is_subscribed(client, message): return await not_joined(client, message)
    await get_video(client, message)

@Bot.on_message(filters.regex("Get Photo 📸"))
async def on_get_photo(client: Client, message: Message):
    if await db.ban_user_exist(message.from_user.id): return await message.reply_text(BAN_TXT, quote=True)
    if not await is_subscribed(client, message): return await not_joined(client, message)
    await get_photo(client, message)

@Bot.on_message(filters.regex("Get Batch 📦"))
async def on_get_batch(client: Client, message: Message):
    if await db.ban_user_exist(message.from_user.id): return await message.reply_text(BAN_TXT, quote=True)
    if not await is_subscribed(client, message): return await not_joined(client, message)
    await get_batch(client, message)

# --- Media Handlers ---
async def store_videos(app: Client):
    all_videos = []
    messages = await try_until_get(app.get_messages(CHANNEL_ID, VIDEOS_RANGE))
    for msg in messages:
        if msg and msg.video:
            if not await db.video_exists(msg.video.file_id):
                all_videos.append({"file_id": msg.video.file_id})
    if all_videos: await db.insert_videos(all_videos)

async def store_photos(app: Client):
    all_photos = []
    messages = await try_until_get(app.get_messages(CHANNEL_ID, VIDEOS_RANGE))
    for msg in messages:
        if msg and msg.photo:
            if not await db.photo_exists(msg.photo.file_id):
                all_photos.append({"file_id": msg.photo.file_id})
    if all_photos: await db.insert_photos(all_photos)

async def send_random_video(client, chat_id, protect=True, caption="", reply_markup=None, hide_caption=False):
    vids = await db.get_videos()
    if not vids: return None
    final_caption = "" if hide_caption else (caption or None)
    return await client.send_video(chat_id, random.choice(vids)["file_id"], caption=final_caption, reply_markup=reply_markup, protect_content=protect)

async def send_random_photo(client, chat_id, protect=True, caption="", reply_markup=None, hide_caption=False):
    photos = await db.get_photos()
    if not photos: return None
    final_caption = "" if hide_caption else (caption or None)
    return await client.send_photo(chat_id, random.choice(photos)["file_id"], caption=final_caption, reply_markup=reply_markup, protect_content=protect)

async def get_photo(client: Client, message: Message):
    user_id = message.from_user.id
    is_allowed, rem = await db.check_spam_limit(user_id, "get_photo")
    if not is_allowed: return await message.reply_text(f"⏳ Wait {rem}s.")

    is_prem = await is_premium_user(user_id)
    if not is_prem:
        free_limit = await db.get_free_limit(user_id)
        if await db.check_free_usage(user_id) >= free_limit:
            return await message.reply_text("Free limit reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Premium", callback_data="buy_prem")]]))
        await db.update_free_usage(user_id)

    auto_del = await db.get_auto_delete()
    timer = await db.get_del_timer()
    hide = await db.get_hide_caption()
    protect = await db.get_protect_content()
    caption = await db.get_custom_caption() or CUSTOM_CAPTION
    markup = await get_btn_markup()

    sent = await send_random_photo(client, message.chat.id, protect=protect, caption=caption, reply_markup=markup, hide_caption=hide)
    if auto_del and sent: asyncio.create_task(auto_del_notification(client.username, sent, timer, f"get_photo_{user_id}"))

async def get_video(client: Client, message: Message):
    user_id = message.from_user.id
    is_allowed, rem = await db.check_spam_limit(user_id, "get_video")
    if not is_allowed: return await message.reply_text(f"⏳ Wait {rem}s.")

    is_prem = await is_premium_user(user_id)
    if not is_prem:
        free_limit = await db.get_free_limit(user_id)
        if await db.check_free_usage(user_id) >= free_limit:
            return await message.reply_text("Free limit reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Premium", callback_data="buy_prem")]]))
        await db.update_free_usage(user_id)

    auto_del = await db.get_auto_delete()
    timer = await db.get_del_timer()
    hide = await db.get_hide_caption()
    protect = await db.get_protect_content()
    caption = await db.get_custom_caption() or CUSTOM_CAPTION
    markup = await get_btn_markup()

    sent = await send_random_video(client, message.chat.id, protect=protect, caption=caption, reply_markup=markup, hide_caption=hide)
    if auto_del and sent: asyncio.create_task(auto_del_notification(client.username, sent, timer, f"get_video_{user_id}"))

async def get_batch(client: Client, message: Message):
    user_id = message.from_user.id
    is_allowed, rem = await db.check_spam_limit(user_id, "get_batch", 3, 120)
    if not is_allowed: return await message.reply_text(f"⏳ Wait {rem}s.")

    is_prem = await is_premium_user(user_id)
    if not is_prem:
        free_limit = await db.get_free_limit(user_id)
        if await db.check_free_usage(user_id) >= free_limit:
            return await message.reply_text("Free limit reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Premium", callback_data="buy_prem")]]))
        await db.update_free_usage(user_id)

    auto_del = await db.get_auto_delete()
    timer = await db.get_del_timer()
    hide = await db.get_hide_caption()
    protect = await db.get_protect_content()
    caption = await db.get_custom_caption() or CUSTOM_CAPTION

    sent_msgs = await send_batch_media(client, message.chat.id, protect=protect, caption=caption, hide_caption=hide)
    if auto_del and sent_msgs:
        last = sent_msgs[-1] if isinstance(sent_msgs, list) else sent_msgs
        asyncio.create_task(auto_del_notification(client.username, last, timer, f"get_batch_{user_id}", is_batch=True, all_messages=sent_msgs if isinstance(sent_msgs, list) else [sent_msgs]))

async def send_batch_media(client: Client, chat_id, protect=True, caption=None, hide_caption=False):
    photos = await db.get_photos()
    videos = await db.get_videos()
    all_media = [("photo", p["file_id"]) for p in photos] + [("video", v["file_id"]) for v in videos]
    if not all_media: return None
    random.shuffle(all_media)
    selected = all_media[:10]

    media_group = []
    for idx, (mtype, fid) in enumerate(selected):
        cap = caption if idx == 0 and not hide_caption else None
        if mtype == "photo": media_group.append(InputMediaPhoto(fid, caption=cap))
        else: media_group.append(InputMediaVideo(fid, caption=cap))

    return await client.send_media_group(chat_id, media_group, protect_content=protect)

async def try_until_get(func):
    try: return await func
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await try_until_get(func)
    except: return []

async def not_joined(client: Client, message: Message):
    buttons = []
    for chat_id in await db.get_all_channels():
        if not await is_userJoin(client, message.from_user.id, chat_id):
            try:
                chat = await client.get_chat(chat_id)
                buttons.append([InlineKeyboardButton(chat.title, url=chat.invite_link or (await client.export_chat_invite_link(chat_id)))])
            except: pass
    buttons.append([InlineKeyboardButton("Close ✖️", callback_data="close")])
    force_msg_db = await db.get_force_msg()
    await message.reply_photo(photo=FORCE_PIC, caption=(force_msg_db or FORCE_MSG).format(mention=message.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons))


# --- Admin Sync Command ---
@Bot.on_message(filters.command("sync") & filters.private & is_admin)
async def sync_media_command(client: Client, message: Message):
    msg = await message.reply("🔄 <b>Syncing media from channel...</b>\nThis might take a while depending on the range.", quote=True)
    try:
        await store_photos(client)
        await store_videos(client)
        await msg.edit("✅ <b>Media synced successfully!</b>")
    except Exception as e:
        await msg.edit(f"❌ <b>Sync failed:</b> {e}")

# --- Admin Status Command ---
@Bot.on_message(filters.command('status') & filters.private & is_admin)
async def status_command(client: Bot, message: Message):
    start_time = time.time()
    temp_msg = await message.reply("<b><i>Processing...</i></b>", quote=True)
    ping_time = (time.time() - start_time) * 1000

    users = await db.full_userbase()

    try:
        now = datetime.now(IST)
        if hasattr(client, 'uptime') and client.uptime:
            uptime = client.uptime
            if uptime.tzinfo is None: uptime = IST.localize(uptime)
            delta = now - uptime
            bottime = get_readable_time(int(delta.total_seconds()))
        else: bottime = "N/A"
    except: bottime = "N/A"

    await temp_msg.edit(
        f"<b>Users: {len(users)}\n\n"
        f"Uptime: {bottime}\n\n"
        f"Ping: {ping_time:.2f} ms</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]])
    )


# --- Broadcast Command with Progress ---
cancel_lock = asyncio.Lock()
is_canceled = False

@Bot.on_message(filters.command('cancel') & filters.private & is_admin)
async def cancel_broadcast(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True
    await message.reply("Broadcast canceling...")

@Bot.on_message(filters.private & filters.command('broadcast') & is_admin)
async def broadcast_command(client: Bot, message: Message):
    global is_canceled
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast.")

    args = message.text.split()[1:]
    do_pin = "pin" in [a.lower() for a in args]

    async with cancel_lock:
        is_canceled = False

    query = await db.full_userbase()
    broadcast_msg = message.reply_to_message
    total = len(query)
    successful = blocked = deleted = unsuccessful = 0

    pls_wait = await message.reply(f"<i>Broadcasting...</i>")

    for i, chat_id in enumerate(query, start=1):
        async with cancel_lock:
            if is_canceled:
                await pls_wait.edit(f"›› BROADCAST CANCELED ❌")
                return

        try:
            sent_msg = await broadcast_msg.copy(chat_id)
            if do_pin: await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent_msg = await broadcast_msg.copy(chat_id)
                if do_pin: await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
                successful += 1
            except: unsuccessful += 1
        except UserIsBlocked:
            await db.del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await db.del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1

        if i % 20 == 0 or i == total:
            await pls_wait.edit(f"<b>›› BROADCAST IN PROGRESS...</b>\n\nTotal: {total}\nSuccess: {successful}\nBlocked: {blocked}")

    await pls_wait.edit(f"<b>›› BROADCAST COMPLETED ✅</b>\n\nTotal: {total}\nSuccess: {successful}\nBlocked: {blocked}\nDeleted: {deleted}")
