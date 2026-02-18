
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.errors.pyromod import ListenerTimeout
from bot import Bot
from config import OWNER_ID, START_PIC, PICS
from database.database import db
from helper_func import is_admin
import random
import asyncio
import logging
from plugins.FORMATS import *
from plugins.autoDelete import convert_time

# Centralized Settings for the Bot
# Managed by @rohit_1888

async def get_settings_markup():
    buttons = [
        [InlineKeyboardButton("ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs", callback_data="set_fsub"), InlineKeyboardButton("ᴀᴅᴍɪɴs & ʙᴀɴs", callback_data="set_users")],
        [InlineKeyboardButton("ғɪʟᴇ sᴇᴛᴛɪɴɢs", callback_data="set_files"), InlineKeyboardButton("sʜᴏʀᴛᴇɴᴇʀ", callback_data="set_shortener")],
        [InlineKeyboardButton("ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="set_autodel"), InlineKeyboardButton("ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ", callback_data="set_caption_menu")],
        [InlineKeyboardButton("ᴛᴇxᴛs & ᴘʜᴏᴛᴏs", callback_data="set_texts"), InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs 📜", callback_data="view_commands")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
    ]
    return InlineKeyboardMarkup(buttons)

@Bot.on_message((filters.command("settings") | filters.regex("^Settings ⚙️$")) & filters.private & is_admin)
async def settings_command(client, message):
    logging.info(f"Settings command triggered by {message.from_user.id}")
    total_fsub = len(await db.get_all_channels())
    total_admin = len(await db.get_all_admins())
    total_ban = len(await db.get_ban_users())
    autodel_mode = 'Eɴᴀʙʟᴇᴅ' if await db.get_auto_delete() else 'Dɪsᴀʙʟᴇᴅ'
    protect_content = 'Eɴᴀʙʟᴇᴅ' if await db.get_protect_content() else 'Dɪsᴀʙʟᴇᴅ'
    hide_caption = 'Eɴᴀʙʟᴇᴅ' if await db.get_hide_caption() else 'Dɪsᴀʙʟᴇᴅ'
    chnl_butn = 'Eɴᴀʙʟᴇᴅ' if await db.get_channel_button() else 'Dɪsᴀʙʟᴇᴅ'
    reqfsub = 'Eɴᴀʙʟᴇᴅ' if await db.get_request_forcesub() else 'Dɪsᴀʙʟᴇᴅ'

    msg = SETTING_TXT.format(
        total_fsub=total_fsub,
        total_admin=total_admin,
        total_ban=total_ban,
        autodel_mode=autodel_mode,
        protect_content=protect_content,
        hide_caption=hide_caption,
        chnl_butn=chnl_butn,
        reqfsub=reqfsub
    )
    
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=msg,
        reply_markup=await get_settings_markup()
    )

@Bot.on_callback_query(filters.regex("^settings$"))
async def settings_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    
    total_fsub = len(await db.get_all_channels())
    total_admin = len(await db.get_all_admins())
    total_ban = len(await db.get_ban_users())
    autodel_mode = 'Eɴᴀʙʟᴇᴅ' if await db.get_auto_delete() else 'Dɪsᴀʙʟᴇᴅ'
    protect_content = 'Eɴᴀʙʟᴇᴅ' if await db.get_protect_content() else 'Dɪsᴀʙʟᴇᴅ'
    hide_caption = 'Eɴᴀʙʟᴇᴅ' if await db.get_hide_caption() else 'Dɪsᴀʙʟᴇᴅ'
    chnl_butn = 'Eɴᴀʙʟᴇᴅ' if await db.get_channel_button() else 'Dɪsᴀʙʟᴇᴅ'
    reqfsub = 'Eɴᴀʙʟᴇᴅ' if await db.get_request_forcesub() else 'Dɪsᴀʙʟᴇᴅ'

    msg = SETTING_TXT.format(
        total_fsub=total_fsub,
        total_admin=total_admin,
        total_ban=total_ban,
        autodel_mode=autodel_mode,
        protect_content=protect_content,
        hide_caption=hide_caption,
        chnl_butn=chnl_butn,
        reqfsub=reqfsub
    )
    
    await query.edit_message_caption(
        caption=msg,
        reply_markup=await get_settings_markup()
    )

# --- Force Sub Settings ---
@Bot.on_callback_query(filters.regex("^set_fsub$"))
async def set_fsub_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    channels = await db.get_all_channels()
    channel_list = ""
    if channels:
        for i, ch_id in enumerate(channels, 1):
            try:
                chat = await client.get_chat(ch_id)
                channel_list += f"{i}. {chat.title} (`{ch_id}`)\n"
            except:
                channel_list += f"{i}. Unknown (`{ch_id}`)\n"
    else:
        channel_list = "No channels added."

    msg = f"<b>📢 Force Sub Channels:</b>\n\n{channel_list}\n"
    msg += f"Request FSub Mode: {'Eɴᴀʙʟᴇᴅ' if await db.get_request_forcesub() else 'Dɪsᴀʙʟᴇᴅ'}"

    buttons = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data="add_fsub_btn"), InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", callback_data="rm_fsub_btn")],
        [InlineKeyboardButton("ᴛᴏɢɢʟᴇ ʀᴇǫᴜᴇsᴛ ᴍᴏᴅᴇ", callback_data="toggle_req_fsub")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^toggle_req_fsub$"))
async def toggle_req_fsub(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    curr = await db.get_request_forcesub()
    await db.set_request_forcesub(not curr)
    await set_fsub_callback(client, query)

@Bot.on_callback_query(filters.regex("^add_fsub_btn$"))
async def add_fsub_callback(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner Only!", show_alert=True)
    
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the Channel ID to add as Force Sub:", timeout=60)
        ch_id = int(ask.text)
        await db.add_channel(ch_id)
        await ask.reply(f"✅ Channel `{ch_id}` added successfully!")
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "Timeout! Please try again.")
    except Exception as e:
        await client.send_message(query.from_user.id, f"Error: {e}")
    
    # Re-send settings
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^rm_fsub_btn$"))
async def rm_fsub_callback(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner Only!", show_alert=True)
    
    channels = await db.get_all_channels()
    if not channels:
        return await query.answer("No channels to remove!", show_alert=True)
    
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the Channel ID to remove from Force Sub:", timeout=60)
        ch_id = int(ask.text)
        await db.del_channel(ch_id)
        await ask.reply(f"✅ Channel `{ch_id}` removed successfully!")
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "Timeout! Please try again.")
    except Exception as e:
        await client.send_message(query.from_user.id, f"Error: {e}")
    
    await settings_command(client, query.message)

# --- Admin & Ban Settings ---
@Bot.on_callback_query(filters.regex("^set_users$"))
async def set_users_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    admins = await db.get_all_admins()
    bans = await db.get_ban_users()
    
    msg = f"<b>👥 Admin & Ban Management</b>\n\n"
    msg += f"Admins: `{len(admins)}` (excluding owner)\n"
    msg += f"Banned Users: `{len(bans)}`"
    
    buttons = [
        [InlineKeyboardButton("ᴍᴀɴᴀɢᴇ ᴀᴅᴍɪɴs", callback_data="manage_admins"), InlineKeyboardButton("ᴍᴀɴᴀɢᴇ ʙᴀɴs", callback_data="manage_bans")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^manage_admins$"))
async def manage_admins(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner Only!", show_alert=True)
    
    admins = await db.get_all_admins()
    admin_list = "\n".join([f"- `{a}`" for a in admins]) if admins else "No extra admins."
    
    msg = f"<b>🛡️ Admin List:</b>\n\n{admin_list}"
    buttons = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴀᴅᴍɪɴ", callback_data="add_admin_btn"), InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ", callback_data="rm_admin_btn")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="set_users")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^add_admin_btn$"))
async def add_admin_callback(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner Only!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the User ID to add as Admin:", timeout=60)
        user_id = int(ask.text)
        await db.add_admin(user_id)
        await ask.reply(f"✅ User `{user_id}` added as Admin!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^rm_admin_btn$"))
async def rm_admin_callback(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Owner Only!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the User ID to remove from Admins:", timeout=60)
        user_id = int(ask.text)
        await db.del_admin(user_id)
        await ask.reply(f"✅ User `{user_id}` removed from Admins!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^manage_bans$"))
async def manage_bans(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    bans = await db.get_ban_users()
    ban_list = f"Total Banned: `{len(bans)}`"
    
    msg = f"<b>🚫 Banned Users</b>\n\n{ban_list}"
    buttons = [
        [InlineKeyboardButton("ʙᴀɴ ᴜsᴇʀ", callback_data="add_ban_btn"), InlineKeyboardButton("ᴜɴʙᴀɴ ᴜsᴇʀ", callback_data="rm_ban_btn")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="set_users")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^add_ban_btn$"))
async def add_ban_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the User ID to Ban:", timeout=60)
        user_id = int(ask.text)
        await db.add_ban_user(user_id)
        await ask.reply(f"✅ User `{user_id}` Banned!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^rm_ban_btn$"))
async def rm_ban_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send the User ID to Unban:", timeout=60)
        user_id = int(ask.text)
        await db.del_ban_user(user_id)
        await ask.reply(f"✅ User `{user_id}` Unbanned!")
    except:
        pass
    await settings_command(client, query.message)

# --- File Settings ---
@Bot.on_callback_query(filters.regex("^set_files$"))
async def set_files_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    protect = await db.get_protect_content()
    hide_caption = await db.get_hide_caption()
    chnl_btn = await db.get_channel_button()
    name1, link1, name2, link2 = await db.get_channel_button_links()

    msg = FILES_CMD_TXT.format(
        protect_content="Enabled ✅" if protect else "Disabled ❌",
        hide_caption="Enabled ✅" if hide_caption else "Disabled ❌",
        channel_button="Enabled ✅" if chnl_btn else "Disabled ❌",
        name=name1 or "Not Set",
        link=link1 or "Not Set",
        name2=name2 or "Not Set",
        link2=link2 or "Not Set"
    )

    buttons = [
        [InlineKeyboardButton(f"ᴘʀᴏᴛᴇᴄᴛ: {'✅' if protect else '❌'}", callback_data="toggle_protect"),
         InlineKeyboardButton(f"ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ: {'✅' if hide_caption else '❌'}", callback_data="toggle_hc")],
        [InlineKeyboardButton(f"ʙᴜᴛᴛᴏɴ: {'✅' if chnl_btn else '❌'}", callback_data="toggle_cb"),
         InlineKeyboardButton("sᴇᴛ ʙᴜᴛᴛᴏɴs", callback_data="set_btn_links")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^toggle_protect$"))
async def toggle_protect(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    curr = await db.get_protect_content()
    await db.set_protect_content(not curr)
    await set_files_callback(client, query)

@Bot.on_callback_query(filters.regex("^toggle_hc$"))
async def toggle_hc(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    curr = await db.get_hide_caption()
    await db.set_hide_caption(not curr)
    await set_files_callback(client, query)

@Bot.on_callback_query(filters.regex("^toggle_cb$"))
async def toggle_cb(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    curr = await db.get_channel_button()
    await db.set_channel_button(not curr)
    await set_files_callback(client, query)

@Bot.on_callback_query(filters.regex("^set_btn_links$"))
async def set_btn_links(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        example = "Format:\n1 Button: `Name - Link`\n2 Buttons: `Name1 - Link1 | Name2 - Link2`"
        ask = await client.ask(query.from_user.id, f"Send Button Details:\n\n{example}", timeout=60)
        text = ask.text
        if "|" in text:
            parts = text.split("|")
            b1 = parts[0].split("-")
            b2 = parts[1].split("-")
            await db.set_channel_button_links(b1[0].strip(), b1[1].strip(), b2[0].strip(), b2[1].strip())
        else:
            b1 = text.split("-")
            await db.set_channel_button_links(b1[0].strip(), b1[1].strip())
        await ask.reply("✅ Buttons set successfully!")
    except:
        pass
    await settings_command(client, query.message)

# --- Shortener Settings ---
@Bot.on_callback_query(filters.regex("^set_shortener$"))
async def set_shortener_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    url = await db.get_shortener_url()
    api = await db.get_shortener_api()
    v_time = await db.get_verified_time()
    tut = await db.get_tut_video()

    msg = f"<b>🔗 Shortener Settings</b>\n\n"
    msg += f"Site: `{url or 'Not Set'}`\n"
    msg += f"API: `{api or 'Not Set'}`\n"
    msg += f"Verify Time: `{v_time or 'Not Set'}` seconds\n"
    msg += f"Tutorial: [Link]({tut})" if tut else "Tutorial: Not Set"

    buttons = [
        [InlineKeyboardButton("sᴇᴛ sɪᴛᴇ & ᴀᴘɪ", callback_data="set_short_api"), InlineKeyboardButton("sᴇᴛ ᴠᴇʀɪғʏ ᴛɪᴍᴇ", callback_data="set_v_time")],
        [InlineKeyboardButton("sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ", callback_data="set_tut_link"), InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data="disable_short")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^set_short_api$"))
async def set_short_api(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send Shortener Site URL:", timeout=60)
        url = ask.text.strip()
        ask2 = await client.ask(query.from_user.id, "Send Shortener API Key:", timeout=60)
        api = ask2.text.strip()
        await db.set_shortener_url(url)
        await db.set_shortener_api(api)
        await ask2.reply("✅ Shortener details updated!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^set_v_time$"))
async def set_v_time(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send Verify Time in seconds:", timeout=60)
        await db.set_verified_time(int(ask.text))
        await ask.reply("✅ Verify time updated!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^set_tut_link$"))
async def set_tut_link(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send Tutorial Video Link:", timeout=60)
        await db.set_tut_video(ask.text.strip())
        await ask.reply("✅ Tutorial link updated!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^disable_short$"))
async def disable_short(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await db.deactivate_shortener()
    await query.answer("Shortener Disabled!")
    await set_shortener_callback(client, query)

# --- Auto Delete Settings ---
@Bot.on_callback_query(filters.regex("^set_autodel$"))
async def set_autodel_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    mode = await db.get_auto_delete()
    timer = await db.get_del_timer()

    msg = AUTODEL_CMD_TXT.format(
        autodel_mode="Enabled ✅" if mode else "Disabled ❌",
        timer=convert_time(timer)
    )

    buttons = [
        [InlineKeyboardButton(f"ᴍᴏᴅᴇ: {'✅' if mode else '❌'}", callback_data="toggle_autodel"),
         InlineKeyboardButton("sᴇᴛ ᴛɪᴍᴇʀ", callback_data="set_del_timer_btn")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^toggle_autodel$"))
async def toggle_autodel(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    curr = await db.get_auto_delete()
    await db.set_auto_delete(not curr)
    await set_autodel_callback(client, query)

@Bot.on_callback_query(filters.regex("^set_del_timer_btn$"))
async def set_del_timer_btn(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send Delete Timer in seconds:", timeout=60)
        await db.set_del_timer(int(ask.text))
        await ask.reply("✅ Delete timer updated!")
    except:
        pass
    await settings_command(client, query.message)

# --- Custom Caption Settings ---
@Bot.on_callback_query(filters.regex("^set_caption_menu$"))
async def set_caption_menu(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    caption = await db.get_custom_caption()

    msg = f"<b>📝 Custom Caption Settings</b>\n\n"
    msg += f"Current Caption:\n<pre>{caption or 'Not Set'}</pre>"

    buttons = [
        [InlineKeyboardButton("sᴇᴛ ᴄᴀᴘᴛɪᴏɴ", callback_data="add_caption_btn"), InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ", callback_data="rm_caption_btn")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^add_caption_btn$"))
async def add_caption_btn(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, "Send your Custom Caption text:", timeout=120)
        await db.set_custom_caption(ask.text)
        await ask.reply("✅ Custom caption updated!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^rm_caption_btn$"))
async def rm_caption_btn(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await db.set_custom_caption(None)
    await query.answer("Caption Removed!")
    await set_caption_menu(client, query)

# --- Texts & Photos Settings (Simplified) ---
@Bot.on_callback_query(filters.regex("^set_texts$"))
async def set_texts_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    msg = "<b>📝 Texts & Photos Configuration</b>\n\nUse buttons below to change bot messages and images."
    buttons = [
        [InlineKeyboardButton("sᴛᴀʀᴛ ᴍsɢ", callback_data="edit_txt_start"), InlineKeyboardButton("ғsᴜʙ ᴍsɢ", callback_data="edit_txt_fsub")],
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]
    ]
    await query.edit_message_caption(caption=msg, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex("^edit_txt_start$"))
async def edit_txt_start(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    msg = await db.get_start_msg() or START_MSG
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, f"<b>Current Start Message:</b>\n\n<code>{msg}</code>\n\nSend a new message to change it:", timeout=300)
        if ask.text:
            await db.set_start_msg(ask.text)
            await ask.reply("✅ Start Message updated!")
    except:
        pass
    await settings_command(client, query.message)

@Bot.on_callback_query(filters.regex("^view_commands$"))
async def view_commands_callback(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    await query.edit_message_caption(
        caption=CMD_TXT + "\n\n<b>/sync</b> : Sync media from channel\n<b>/settings</b> : Open this menu",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings")]])
    )

@Bot.on_callback_query(filters.regex("^edit_txt_fsub$"))
async def edit_txt_fsub(client, query):
    if not await is_admin(client, query):
        return await query.answer("❌ Access Denied!", show_alert=True)
    msg = await db.get_force_msg() or FORCE_MSG
    await query.message.delete()
    try:
        ask = await client.ask(query.from_user.id, f"<b>Current Force Sub Message:</b>\n\n<code>{msg}</code>\n\nSend a new message to change it:", timeout=300)
        if ask.text:
            await db.set_force_msg(ask.text)
            await ask.reply("✅ Force Sub Message updated!")
    except:
        pass
    await settings_command(client, query.message)
