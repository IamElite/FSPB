import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNELS, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
#----Token
from shortzy import Shortzy
import requests
import time
from datetime import datetime
from database.database import user_data, db_verify_status, db_update_verify_status


async def is_subscribed(_, client, message):
    user_id = message.from_user.id

    if user_id in ADMINS:
        return True

    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                return False
        except (UserNotParticipant, PeerIdInvalid):
            return False
        except Exception as e:
            print(f"Subscription check failed: {e}")
            continue

    return True

used_invites = {}

def is_invite_used(user_id, channel_id):
    return used_invites.get(user_id, {}).get(channel_id, False)

def mark_invite_used(user_id, channel_id):
    if user_id not in used_invites:
        used_invites[user_id] = {}
    used_invites[user_id][channel_id] = True


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

async def encode_premium(vipstring):
    # Double encoding for premium links
    first_encoding = await encode(vipstring)
    second_encoding = await encode(first_encoding)
    return second_encoding

async def decode_premium(second_encoding):
    # Double decoding for premium links
    first_decoding = await decode(second_encoding)
    second_decoding = await decode(first_decoding)
    return second_decoding

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

async def get_verify_status(user_id):
    verify = await db_verify_status(user_id)
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link=""):
    current = await db_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    await db_update_verify_status(user_id, current)


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

subscribed = filters.create(is_subscribed)
