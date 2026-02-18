
import time
import os
import motor.motor_asyncio
from config import DB_URI, DB_NAME
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

class Rohit:

    def __init__(self, uri, name):
        self.uri = uri
        self.name = name
        if not uri:
            self.dbclient = None
            self.database = None
        else:
            self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self.database = self.dbclient[name]

        if self.database is not None:
            self.channel_data = self.database['channels']
            self.admins_data = self.database['admins']
            self.user_data = self.database['users']
            self.banned_user_data = self.database['banned_user']
            self.autho_user_data = self.database['autho_user']
            self.shortener_data = self.database['shortener']
            self.settings_data = self.database['settings']
            self.free_data = self.database['free']
            self.for_data = self.database['for']
            self.login_data = self.database['login']
            self.auto_delete_data = self.database['auto_delete']
            self.hide_caption_data = self.database['hide_caption']
            self.protect_content_data = self.database['protect_content']
            self.channel_button_data = self.database['channel_button']
            self.del_timer_data = self.database['del_timer']
            self.channel_button_link_data = self.database['channelButton_link']
            self.custom_caption_data = self.database['custom_caption']
            self.rqst_fsub_data = self.database['request_forcesub']
            self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
            self.store_reqLink_data = self.database['store_reqLink']
            self.videos_collection = self.database["vids"]
            self.photos_collection = self.database["pics"]
            self.users_collection = self.database["user_subs"]
            self.spam_protection_data = self.database["spam_protection"]
            self.referrals_collection = self.database["referrals"]
            self.collection = self.database['premium-users'] # For compatibility with db_premium

    def _check_db(self):
        if not self.uri or self.database is None:
            raise RuntimeError("Database not initialized. Check your DB_URI in configuration.")

    # Shortener Token
    async def set_shortener_url(self, url):
        self._check_db()
        try:
            existing = await self.shortener_data.find_one({"active": True})
            if existing:
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"shortener_url": url, "updated_at": datetime.utcnow()}}
                )
            else:
                await self.shortener_data.insert_one({
                    "shortener_url": url,
                    "api_key": None,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener URL: {e}")
            return False

    async def set_shortener_api(self, api):
        self._check_db()
        try:
            existing = await self.shortener_data.find_one({"active": True})
            if existing:
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"api_key": api, "updated_at": datetime.utcnow()}}
                )
            else:
                await self.shortener_data.insert_one({
                    "shortener_url": None,
                    "api_key": api,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener API key: {e}")
            return False

    async def get_shortener_url(self):
        self._check_db()
        try:
            shortener = await self.shortener_data.find_one({"active": True}, {"_id": 0, "shortener_url": 1})
            return shortener.get("shortener_url") if shortener else None
        except Exception as e:
            logging.error(f"Error fetching shortener URL: {e}")
            return None

    async def get_shortener_api(self):
        self._check_db()
        try:
            shortener = await self.shortener_data.find_one({"active": True}, {"_id": 0, "api_key": 1})
            return shortener.get("api_key") if shortener else None
        except Exception as e:
            logging.error(f"Error fetching shortener API key: {e}")
            return None


    async def deactivate_shortener(self):
        self._check_db()
        try:
            await self.shortener_data.update_many({"active": True}, {"$set": {"active": False}})
            return True
        except Exception as e:
            logging.error(f"Error deactivating shorteners: {e}")
            return False

    async def set_verified_time(self, verified_time: int):
        self._check_db()
        try:
            await self.settings_data.update_one(
                {"_id": "verified_time"},
                {"$set": {"verified_time": verified_time}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error updating verified time: {e}")
            return False

    async def get_verified_time(self):
        self._check_db()
        try:
            settings = await self.settings_data.find_one({"_id": "verified_time"})
            return settings.get("verified_time", None) if settings else None
        except Exception as e:
            logging.error(f"Error fetching verified time: {e}")
            return None

    async def set_tut_video(self, video_url: str):
        self._check_db()
        try:
            await self.settings_data.update_one(
                {"_id": "tutorial_video"},
                {"$set": {"tutorial_video_url": video_url}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error updating tutorial video URL: {e}")
            return False

    async def get_tut_video(self):
        self._check_db()
        try:
            settings = await self.settings_data.find_one({"_id": "tutorial_video"})
            return settings.get("tutorial_video_url", None) if settings else None
        except Exception as e:
            logging.error(f"Error fetching tutorial video URL: {e}")
            return None

    # USER MANAGEMENT
    async def present_user(self, user_id: int):
        self._check_db()
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        self._check_db()
        await self.user_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

    async def full_userbase(self):
        self._check_db()
        user_docs = await self.user_data.find().to_list(length=None)
        return [doc['_id'] for doc in user_docs]

    async def del_user(self, user_id: int):
        self._check_db()
        await self.user_data.delete_one({'_id': user_id})

    # VERIFICATION MANAGEMENT
    async def get_verify_status(self, user_id):
        self._check_db()
        default_verify = {
            'is_verified': False,
            'verified_time': 0,
            'verify_token': "",
            'link': ""
        }
        user = await self.user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
        return default_verify

    async def update_verify_status(self, user_id, verify_token="", is_verified=False, verified_time=0, link=""):
        self._check_db()
        current = await self.get_verify_status(user_id)
        current['verify_token'] = verify_token
        current['is_verified'] = is_verified
        current['verified_time'] = verified_time
        current['link'] = link
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': current}}, upsert=True)

    # CHANNEL BUTTON SETTINGS
    async def set_channel_button_links(self, button_name: str, button_link: str, button_name2: str = None, button_link2: str = None):
        self._check_db()
        data = {'button_name': button_name, 'button_link': button_link}
        if button_name2 and button_link2:
            data['button_name2'] = button_name2
            data['button_link2'] = button_link2
        await self.channel_button_link_data.delete_many({})
        await self.channel_button_link_data.insert_one(data)

    async def get_channel_button_links(self):
        self._check_db()
        data = await self.channel_button_link_data.find_one({})
        if data:
            return (
                data.get('button_name'), data.get('button_link'),
                data.get('button_name2'), data.get('button_link2')
            )
        return ' Channel', 'https://t.me/rohit_1888', None, None

    # DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):
        self._check_db()
        await self.del_timer_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def get_del_timer(self):
        self._check_db()
        data = await self.del_timer_data.find_one({})
        return data.get('value', 600) if data else 600

    # BOOLEAN SETTINGS
    async def set_auto_delete(self, value: bool):
        self._check_db()
        await self.auto_delete_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def set_hide_caption(self, value: bool):
        self._check_db()
        await self.hide_caption_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def set_protect_content(self, value: bool):
        self._check_db()
        await self.protect_content_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def set_channel_button(self, value: bool):
        self._check_db()
        await self.channel_button_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def set_request_forcesub(self, value: bool):
        self._check_db()
        await self.rqst_fsub_data.update_one({}, {'$set': {'value': value}}, upsert=True)

    async def get_auto_delete(self):
        self._check_db()
        data = await self.auto_delete_data.find_one({})
        return data.get('value', False) if data else False

    async def get_hide_caption(self):
        self._check_db()
        data = await self.hide_caption_data.find_one({})
        return data.get('value', False) if data else False

    async def get_protect_content(self):
        self._check_db()
        data = await self.protect_content_data.find_one({})
        return data.get('value', False) if data else False

    async def get_channel_button(self):
        self._check_db()
        data = await self.channel_button_data.find_one({})
        return data.get('value', False) if data else False

    async def get_request_forcesub(self):
        self._check_db()
        data = await self.rqst_fsub_data.find_one({})
        return data.get('value', False) if data else False

    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        self._check_db()
        found = await self.channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        self._check_db()
        await self.channel_data.update_one({'_id': channel_id}, {'$set': {'_id': channel_id}}, upsert=True)

    async def del_channel(self, channel_id: int):
        self._check_db()
        await self.channel_data.delete_one({'_id': channel_id})

    async def get_all_channels(self):
        self._check_db()
        channel_docs = await self.channel_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    # ADMIN USER MANAGEMENT
    async def admin_exist(self, admin_id: int):
        self._check_db()
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        self._check_db()
        await self.admins_data.update_one({'_id': admin_id}, {'$set': {'_id': admin_id}}, upsert=True)

    async def del_admin(self, admin_id: int):
        self._check_db()
        await self.admins_data.delete_one({'_id': admin_id})

    async def get_all_admins(self):
        self._check_db()
        users_docs = await self.admins_data.find().to_list(length=None)
        return [doc['_id'] for doc in users_docs]


    # BAN USER MANAGEMENT
    async def ban_user_exist(self, user_id: int):
        self._check_db()
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        self._check_db()
        await self.banned_user_data.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)

    async def del_ban_user(self, user_id: int):
        self._check_db()
        await self.banned_user_data.delete_one({'_id': user_id})

    async def get_ban_users(self):
        self._check_db()
        users_docs = await self.banned_user_data.find().to_list(length=None)
        return [doc['_id'] for doc in users_docs]


    # REQUEST FORCE-SUB MANAGEMENT
    async def add_reqChannel(self, channel_id: int):
        self._check_db()
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$setOnInsert': {'user_ids': []}},
            upsert=True
        )

    async def reqChannel_exist(self, channel_id: int):
        self._check_db()
        found = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return bool(found)

    async def reqSent_user(self, channel_id: int, user_id: int):
        self._check_db()
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$addToSet': {'user_ids': user_id}},
            upsert=True
        )

    async def reqSent_user_exist(self, channel_id: int, user_id: int):
        self._check_db()
        found = await self.rqst_fsub_Channel_data.find_one(
            {'_id': channel_id, 'user_ids': user_id}
        )
        return bool(found)

    async def del_reqSent_user(self, channel_id: int, user_id: int):
        self._check_db()
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$pull': {'user_ids': user_id}}
        )

    async def del_reqChannel(self, channel_id: int):
        self._check_db()
        await self.rqst_fsub_Channel_data.delete_one({'_id': channel_id})

    async def get_reqSent_user(self, channel_id: int):
        self._check_db()
        data = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
        return data.get('user_ids', []) if data else []

    async def get_reqChannel(self):
        self._check_db()
        channel_docs = await self.rqst_fsub_Channel_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    async def clear_reqSent_user(self, channel_id: int):
        self._check_db()
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$set': {'user_ids': []}}
        )

    async def get_reqLink_channels(self):
        self._check_db()
        channel_docs = await self.store_reqLink_data.find().to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    async def get_stored_reqLink(self, channel_id: int):
        self._check_db()
        data = await self.store_reqLink_data.find_one({'_id': channel_id})
        return data.get('link') if data else None

    async def store_reqLink(self, channel_id: int, link: str):
        self._check_db()
        await self.store_reqLink_data.update_one(
            {'_id': channel_id},
            {'$set': {'link': link}},
            upsert=True
        )

    async def del_stored_reqLink(self, channel_id: int):
        self._check_db()
        await self.store_reqLink_data.delete_one({'_id': channel_id})


    # FREE USAGE SETTINGS
    async def get_free_settings(self):
        self._check_db()
        settings = await self.free_data.find_one({"_id": "free_usage"})
        if not settings:
            settings = {"limit": 5, "enabled": True}
            await self.free_data.insert_one({"_id": "free_usage", **settings})
        return settings

    async def set_free_limit(self, limit: int):
        self._check_db()
        await self.free_data.update_one({"_id": "free_usage"}, {"$set": {"limit": limit}}, upsert=True)

    async def check_free_usage(self, user_id):
        self._check_db()
        data = await self.free_data.find_one({"user_id": user_id})
        return int(data.get("count", 0)) if data else 0

    async def get_free_limit(self, user_id):
        self._check_db()
        settings = await self.free_data.find_one({"_id": "free_usage"})
        return int(settings.get("limit", 5)) if settings else 5

    async def update_free_usage(self, user_id):
        self._check_db()
        data = await self.free_data.find_one({"user_id": user_id})
        current_time = time.time()
        if not data:
            await self.free_data.insert_one({"user_id": user_id, "count": 1, "last_reset": current_time})
        else:
            if current_time - data.get("last_reset", 0) > 86400:
                await self.free_data.update_one({"user_id": user_id}, {"$set": {"count": 1, "last_reset": current_time}})
            else:
                await self.free_data.update_one({"user_id": user_id}, {"$inc": {"count": 1}})

    async def reset_all_free_usage(self):
        self._check_db()
        await self.free_data.update_many({"user_id": {"$exists": True}}, {"$set": {"count": 0, "last_reset": time.time()}})

    # SPAM PROTECTION
    async def set_spam_notify_flag(self, user_id: int, action_type: str):
        self._check_db()
        key = f"{user_id}_{action_type}"
        await self.spam_protection_data.update_one({"_id": key}, {"$set": {"notify_scheduled": True}}, upsert=True)

    async def clear_spam_notify_flag(self, user_id: int, action_type: str):
        self._check_db()
        key = f"{user_id}_{action_type}"
        await self.spam_protection_data.update_one({"_id": key}, {"$unset": {"notify_scheduled": ""}})

    async def get_spam_notify_flag(self, user_id: int, action_type: str) -> bool:
        self._check_db()
        key = f"{user_id}_{action_type}"
        data = await self.spam_protection_data.find_one({"_id": key})
        return bool(data and data.get("notify_scheduled", False))

    # FREE STATE
    async def get_free_state(self, user_id):
        self._check_db()
        user_data = await self.login_data.find_one({"user_id": user_id})
        return user_data.get("free_state", True) if user_data else True

    async def set_free_state(self, user_id, state):
        self._check_db()
        await self.login_data.update_one({"user_id": user_id}, {"$set": {"free_state": state}}, upsert=True)

    # VIDEO & PHOTO MANAGEMENT
    async def video_exists(self, file_id: str):
        self._check_db()
        return await self.videos_collection.find_one({"file_id": file_id})

    async def insert_videos(self, video_list: list):
        self._check_db()
        if video_list: return await self.videos_collection.insert_many(video_list)

    async def get_videos(self):
        self._check_db()
        return await self.videos_collection.find({}).to_list(length=None)

    async def photo_exists(self, file_id: str):
        self._check_db()
        return await self.photos_collection.find_one({"file_id": file_id})

    async def insert_photos(self, photo_list: list):
        self._check_db()
        if photo_list: return await self.photos_collection.insert_many(photo_list)

    async def get_photos(self):
        self._check_db()
        return await self.photos_collection.find({}).to_list(length=None)

    # SPAM LIMIT
    async def check_spam_limit(self, user_id: int, action_type: str = "default", max_requests: int = 5, time_window: int = 60):
        self._check_db()
        current_time = time.time()
        key = f"{user_id}_{action_type}"
        data = await self.spam_protection_data.find_one({"_id": key})
        if not data:
            await self.spam_protection_data.insert_one({"_id": key, "requests": [current_time]})
            return True, 0
        requests = [r for r in data.get("requests", []) if current_time - r < time_window]
        if len(requests) >= max_requests:
            return False, int(time_window - (current_time - min(requests)))
        requests.append(current_time)
        await self.spam_protection_data.update_one({"_id": key}, {"$set": {"requests": requests}})
        return True, 0

    async def reset_spam_protection(self, user_id: int, action_type: str = "default"):
        self._check_db()
        await self.spam_protection_data.delete_one({"_id": f"{user_id}_{action_type}"})

    # REFERRALS
    async def add_referral(self, referrer_user_id: int, referred_user_id: int):
        self._check_db()
        if await self.referrals_collection.find_one({"referred_user_id": referred_user_id}): return False
        await self.referrals_collection.insert_one({"referrer_user_id": referrer_user_id, "referred_user_id": referred_user_id})
        return True

    async def get_referral_count(self, user_id: int):
        self._check_db()
        return await self.referrals_collection.count_documents({"referrer_user_id": user_id})

    async def check_referral_exists(self, referred_user_id: int):
        self._check_db()
        return bool(await self.referrals_collection.find_one({"referred_user_id": referred_user_id}))

    async def get_referral_stats(self, user_id: int):
        self._check_db()
        total = await self.get_referral_count(user_id)
        return {"total_referrals": total}

    # CUSTOM CAPTION
    async def set_custom_caption(self, caption: str):
        self._check_db()
        await self.custom_caption_data.update_one({"_id": "custom_caption"}, {"$set": {"caption": caption}}, upsert=True)

    async def get_custom_caption(self):
        self._check_db()
        data = await self.custom_caption_data.find_one({"_id": "custom_caption"})
        return data.get("caption") if data else None

# Initialize with fallback for import-time safety
db = Rohit(DB_URI, DB_NAME)
# Compatibility exports
collection = db.collection if db.database is not None else None
