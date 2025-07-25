# https://t.me/ultroid_official

import os
import logging
from logging.handlers import RotatingFileHandler

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "14050586"))
API_HASH = os.environ.get("API_HASH", "42a60d9c657b106370c79bb0a8ac560c")
 
BAN = int(os.environ.get("BAN", "1865273490")) #Owner user id - dont chnge 
OWNER = os.environ.get("OWNER", "DshDm_bot?start") #Owner username
OWNER_ID = int(os.environ.get("OWNER_ID", "7074383232")) #Owner user id
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'OfficialDurgesh')
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "net_pro_max") # WITHOUR @
CHANNEL = os.environ.get("CHANNEL", "net_pro_max") # WITHOUR @

#auto delete
DELETE_AFTER = int(os.environ.get("DELETE_AFTER", '2400')) #seconds
NOTIFICATION_TIME = int(os.environ.get('NOTIFICATION_TIME', 30)) #seconds
AUTO_DELETE = os.environ.get("AUTO_DELETE", False) #ON/OFF
GET_AGAIN = os.environ.get("GET_AGAIN", False) #ON/OFF
DELETE_INFORM = os.environ.get("INFORM" , "Successfully DELETED !!")
NOTIFICATION = os.environ.get("NOTIFICATION" ,"File will delete after 40 minutes.")
GET_INFORM = os.environ.get("GET_INFORM" ,"File was deleted after {DELETE_AFTER} seconds. Use the button below to GET FILE AGAIN.")


#Premium varibles
PAYMENT_QR = os.getenv('PAYMENT_QR', 'https://envs.sh/YfJ.jpg')
PAYMENT_TEXT = os.getenv('PAYMENT_TEXT', '<b>💢 Aᴠᴀɪʟᴀʙʟᴇ Pʟᴀɴs ‼️ \n\n'
                                      '➤ 25ʀs - 1 Wᴇᴇᴋ\n➤ 50ʀs - 15 Dᴀʏꜱ\n'
                                      '➤ 90ʀs - 1 Mᴏɴᴛʜ\n➤ 150ʀs - 2 Mᴏɴᴛʜ\n\n'
                                      '🎁 Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs 🎁\n\n'
                                      '○ Nᴏ Nᴇᴇᴅ Tᴏ ᴠᴇʀɪғʏ\n○ Nᴏ Nᴇᴇᴅ Tᴏ Oᴘᴇɴ Lɪɴᴋ\n'
                                      '○ Dɪʀᴇᴄᴛ Fɪʟᴇs\n○ Aᴅ-Fʀᴇᴇ Exᴘᴇʀɪᴇɴᴄᴇ\n'
                                      '○ Premium Channel Entry\n○ Fᴜʟʟ Aᴅᴍɪɴ Sᴜᴘᴘᴏʀᴛ\n\n'
                                      '✨ Uᴘɪ Iᴅ - <code>lucihere@apl</code>\n\n'
                                      'Cʟɪᴄᴋ Tᴏ Cʜᴇᴄᴋ Yᴏᴜʀ Aᴄᴛɪᴠᴇ Pʟᴀɴ /myplan\n\n'
                                      '💢 Mᴜsᴛ Sᴇɴᴅ Sᴄʀᴇᴇɴsʜᴏᴛ Aғᴛᴇʀ Pᴀʏᴍᴇɴᴛ\n\n'
                                      '‼️ Aғᴛᴇʀ Sᴇɴᴅɪɴɢ Sᴄʀᴇᴇɴsʜᴏᴛ Pʟᴇᴀsᴇ Gɪᴠᴇ Us Sᴏᴍᴇ Tɪᴍᴇ Tᴏ Aᴅᴅ Yᴏᴜ Iɴ Tʜᴇ Pʀᴇᴍɪᴜᴍ</b>')


DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://ar:durgesh@ar.yqov3el.mongodb.net/?retryWrites=true&w=majority&appName=ar")
DB_NAME = os.environ.get("DATABASE_NAME", "ar")
DB_DELETE = os.environ.get("DB_DELETE", "del11")
DB_SHORT = os.environ.get("DB_SHORT", "short11")

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002611158964")) #database save channel id 
LOG_ID = int(os.environ.get("LOG_ID", 0)) #logger id to save logs

# Format: space-separated channel IDs, e.g., "-1002583429026 -1002554824067"
FORCE_SUB_CHANNELS = list(map(int, os.environ.get("FORCE_SUB_CHANNELS", "-1002583429026 -1002554824067").split()))


# 1 page shorner 
SHORT_URL = os.environ.get("SHORT_URL", "teraboxlinks.com") 
SHORT_API = os.environ.get("SHORT_API", "4b7ded045ff9b38818660f6f96995288d6ca59e2")
#Shortner (token system) 
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "shrinkforearn.in") 
SHORTLINK_API = os.environ.get("SHORTLINK_API", "7d14f3e827450b979c653d5fcae203bd85806983")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 43200)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://t.me/Phdlust_Premium_Proof/12")
PR_MSG = os.environ.get("PR_MSG", "https://t.me/Phdlust_Premium_Proof/12")


SHORTCAP = "<b>ᴄʟɪᴄᴋꜱ: {clicks}, 🔗 ʏσᴜʀ ʟɪηᴋ’ꜱ ʀєᴧᴅʏ 👇</b>" #token caption

# ignore this one
SECONDS = int(os.getenv("SECONDS", "200")) # auto delete in seconds

PORT = os.environ.get("PORT", "8080")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))
START_MSG = os.environ.get("START_MESSAGE", """<blockquote>
┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤͟͞●
┆◍ ʜᴇʏ {mention}
┆◍ ɪ'ᴍ : {botmention} 
└──────────────────────•</blockquote><blockquote expandable>
❀ <b>ꜰɪʟє-ᴛσ-ʟɪηᴋ ɢєηєʀᴧᴛσʀ</b> - <i>ᴜᴘʟσᴧᴅ ꜰɪʟєꜱ, ɢєᴛ ɪηꜱᴛᴧηᴛ ᴅɪʀєᴄᴛ ᴅσᴡηʟσᴧᴅ ʟɪηᴋꜱ.</i>
✤ <b>ʟɪηᴋ ϻᴧηᴧɢєʀ</b> – <i>ꜱᴛσʀєꜱ/σʀɢᴧηɪᴢєꜱ ɢʀσᴜᴘ ʟɪηᴋꜱ (ʀᴜʟєꜱ, ʀєꜱσᴜʀᴄєꜱ, єᴛᴄ.).</i>
❃ <b>ᴅᴜᴧʟ-ϻσᴅє</b> – <i>ᴡσʀᴋꜱ �ᴧꜱ ʙσᴛʜ ᴘᴜʙʟɪᴄ ꜰɪʟє-ꜱʜᴧʀɪηɢ ʙσᴛ & ᴘʀɪᴠᴧᴛє ɢʀσᴜᴘ ᴛσσʟ.</i>
✮ <b>ᴧᴜᴛσϻᴧᴛєᴅ</b> – <i>ᴄσϻϻᴧηᴅꜱ ʟɪᴋєʟʏ ꜰσʀ ᴜᴘʟσᴧᴅꜱ, ꜱєᴧʀᴄʜєꜱ, ᴧηᴅ ᴧᴅϻɪη ᴛᴧꜱᴋꜱ.</i></blockquote><blockquote>
•────────────────────────•
 ❖ <b>𝐏ᴏᴡᴇʀᴇᴅ ʙʏ</b> :- <a href="https://t.me/SyntaxRealm">˹ꜱʏηᴛᴧx-ʀєᴧʟϻ ˼ </a> ❤️‍🔥
•────────────────────────•</blockquote>""")

try:
    ADMINS=[7074383232]
    for x in (os.environ.get("ADMINS", "7074383232").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")


FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "<b>🙋‍♂ Hᴇʟʟᴏ,{first}</b>\n➖➖➖➖➖➖➖➖➖➖➖\n<b>🔎 Yᴏᴜ Mᴜsᴛ Nᴇᴇᴅ Tᴏ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟs  Bʏ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴs Iɴ Oʀᴅᴇʀ Tᴏ Usᴇ Mᴇ !!!</b>")

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "~ Join @net_pro_max") # remove None and fo this ->: "here come your txt" also with this " " 

PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "True") == "True" else False

DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", False) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "My mentor, my guide — @DshDm_bot !"

ADMINS.append(OWNER_ID)
ADMINS.append(7074383232)

LOG_FILE_NAME = "uxblogs.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
   





# https://t.me/ultroid_official
