import random
import logging
import asyncio
from bot import Bot
from pyrogram import __version__
from pyrogram.enums import ParseMode
from plugins.FORMATS import *
from config import *
from pyrogram.enums import ChatAction
from database.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Verify user, if he/she is admin or owner before processing the query...
async def authoUser(query, id, owner_only=False):
    if not owner_only:
        if not any([id == OWNER_ID, await db.admin_exist(id)]):
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Aᴅᴍɪɴ !", show_alert=True)
            return False
        return True
    else:
        if id != OWNER_ID:
            await query.answer("❌ Yᴏᴜ ᴀʀᴇ ɴᴏᴛ Oᴡɴᴇʀ !", show_alert=True)
            return False
        return True

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except BaseException:
            pass

    elif data.startswith("get_again_"):
        # Handle get again callback
        try:
            action = data.replace("get_again_", "")
            user_id = query.from_user.id

            parts = action.split("_")
            if len(parts) >= 3:
                action_user_id = int(parts[-1])

                if action_user_id != user_id:
                    await query.answer("❌ Unauthorized access!", show_alert=True)
                    return

                action_type = parts[1]
                await query.answer("🔄 Getting " + action_type + "...")

                msg = query.message
                msg.from_user = query.from_user

                from plugins.start import get_photo, get_video, get_batch
                try:
                    if action_type == "photo":
                        await get_photo(client, msg)
                    elif action_type == "video":
                        await get_video(client, msg)
                    elif action_type == "batch":
                        await get_batch(client, msg)
                    else:
                        await query.answer("❌ Invalid action type!", show_alert=True)
                        return
                finally:
                    try:
                        await query.message.delete()
                    except:
                        pass
            else:
                await query.answer("❌ Invalid format!", show_alert=True)
        except Exception as e:
            logging.error(f"Error handling get_again callback: {e}")
            await query.answer("❌ An error occurred!", show_alert=True)

    elif data == "about":
        await query.message.edit_text(
            text=(
                f"<b>○ Updates : <a href='https://t.me/rohit_1888'>Rohit</a>\n"
                f"○ Language : <code>Python3</code>\n"
                f"○ Library : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⬅️ Bᴀᴄᴋ', callback_data='start'), InlineKeyboardButton(
                    'Cʟᴏsᴇ ✖️', callback_data='close')]
            ]),
        )

    elif data == "buy_prem":
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"👋 {query.from_user.username}\n\n"
                f"🎖️ Available Plans :\n\n"
                f"● {PRICE1}  For 0 Days Prime Membership\n\n"
                f"● {PRICE2}  For 1 Month Prime Membership\n\n"
                f"● {PRICE3}  For 3 Months Prime Membership\n\n"
                f"● {PRICE4}  For 6 Months Prime Membership\n\n"
                f"● {PRICE5}  For 1 Year Prime Membership\n\n\n"
                f"💵 ASK UPI ID TO ADMIN AND PAY THERE -  <code>{UPI_ID}</code>\n\n\n"
                f"♻️ After Payment You Will Get Instant Membership \n\n\n"
                f"‼️ Must Send Screenshot after payment & If anyone want custom time membrship then ask admin"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ADMIN 24/7", url=(SCREENSHOT_URL)
                        )
                    ],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                ]
            )
        )

    elif data == "start":
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS),
                            START_MSG.format(
                                first=query.from_user.first_name,
                                last=query.from_user.last_name,
                                username=None if not query.from_user.username else '@' + query.from_user.username,
                                mention=query.from_user.mention,
                                id=query.from_user.id
            )
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('🤖 Aʙᴏᴜᴛ ᴍᴇ', callback_data='about'), InlineKeyboardButton(
                    'Sᴇᴛᴛɪɴɢs ⚙️', callback_data='settings')]
            ]),
        )
