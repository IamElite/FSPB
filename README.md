<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://dashboard.heroku.com/new?template=https://github.com/IamElite/FSPB"> <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-black?style=for-the-badge&logo=heroku" width="220" height="38.45"/></a></p>



# 📁 UxB-File-Sharing-Premium-Bot

<div align="center" style="border: 2px solid #e94560; border-radius: 10px;">
  <img src="https://yt3.googleusercontent.com/p9g9i5N55WgCn1mFFjl8iut4BOd0O4RRjn7WB_Silj9JmJ42tE-yhdZ0oR_7m-F4kGHT22Br=s176-c-k-c0x00ffffff-no-rj" alt="Bot" width="150" style="border-radius: 10px;">
</div>

<p align="center">
  <a href="https://t.me/ultroid_official">
    <img src="https://img.shields.io/badge/Ultroid%20%F0%9D%95%8F%20Official-Channel-blue?style=for-the-badge&logo=telegram" alt="Ultroid Official Channel">
  </a>
  <a href="https://t.me/ultroidofficial_chat">
    <img src="https://img.shields.io/badge/Ultroid%20%F0%9D%95%8F%20Official-Group-blue?style=for-the-badge&logo=telegram" alt="Ultroid Official Group">
  </a>
</p>

Telegram Bot to store posts and documents accessible via special links.

## 🚀 Overview

File Sharing Token Bot is a Telegram bot designed to store posts and documents, accessible through special links. This bot provides a convenient way to manage and share content within Telegram.

### ✨ Features

- Store posts and documents.
- Access content via special links.
- Easy to deploy and customize.
- 4 Force subs
- Premuim Payment method
- auto delete ( advanced )
- set custom caption
- easy to deploy
  

## 🛠️ Setup

To deploy the bot, follow these steps:

1. Add the bot to a database channel with all permissions.
2. Add the bot to the ForceSub channel as an admin with "Invite Users via Link" permission if ForceSub is enabled.

## 📦 Installation

### Deploy on Heroku


### Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/1jKLr4)

### Deploy on Koyeb

Click the button below to deploy the bot on Koyeb:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/sahildesai07/UxB-file-sharing&branch=main&name=file-sharing-bot)

### Deploy on Your VPS

```bash
git clone https://github.com/sahildesai07/UxB-file-sharing
cd file-sharing-token-bot
pip3 install -r requirements.txt
# <Create config.py appropriately>
python3 main.py
````

### 🔧 Admin Commands

```
start - start the bot or get posts

batch - create link for more than one posts

genlink - create link for one post

users - view bot statistics

broadcast - broadcast any messages to bot users

stats - checking your bot uptime
```

### 🛠️ Variables

* `API_HASH` Your API Hash from my.telegram.org [tutorial video](https://youtu.be/gZQJ-yTMkEo).
* `APP_ID` Your API ID from my.telegram.org [tutorial video](https://youtu.be/gZQJ-yTMkEo).
* `TG_BOT_TOKEN` Your bot token from @BotFather
* `OWNER_ID` Must enter Your Telegram Id
* `CHANNEL_ID` Your Channel ID eg:- -100xxxxxxxx
* `DB_URI ` Your mongo db url [tutorial video](https://youtu.be/qFB0cFqiyOM).
* `DB_NAME` Your mongo db session name
* `ADMINS` Optional: A space separated list of user_ids of Admins, they can only create links
* `START_MSG` Optional: start message of bot, use HTML and <a href='https://github.com/sahildesai07/UxB-file-sharing/blob/main/README.md#start_message'>fillings</a>
* `FORCE_SUB_MESSAGE`Optional:Force sub message of bot, use HTML and Fillings
* `FORCESUB_CHANNEL_1` Optional: ForceSub Channel ID, leave 0 if you want disable force sub
* `FORCESUB_CHANNEL_2` Optional: ForceSub Channel ID, leave 0 if you want disable force sub
* `FORCESUB_CHANNEL_3` Optional: ForceSub Channel ID, leave 0 if you want disable force sub
* `FORCESUB_CHANNEL_4` Optional: ForceSub Channel ID, leave 0 if you want disable force sub
* `PROTECT_CONTENT` Optional: True if you need to prevent files from forwarding

### Extra Variables

* `CUSTOM_CAPTION` put your Custom caption text if you want Setup Custom Caption, you can use HTML and <a href='https://github.com/sahildesai07/UxB-file-sharing/blob/main/README.md#custom_caption'>fillings</a> for formatting (only for documents)
* `DISABLE_CHANNEL_BUTTON` Put True to Disable Channel Share Button, Default if False
* `BOT_STATS_TEXT` put your custom text for stats command, use HTML and <a href='https://github.com/sahildesai07/UxB-file-sharing/blob/main/README.md#custom_stats'>fillings</a>
* `USER_REPLY_TEXT` put your text to show when user sends any message, use HTML

### Fillings
#### START_MESSAGE | FORCE_SUB_MESSAGE

* `{first}` - User first name
* `{last}` - User last name
* `{id}` - User ID
* `{mention}` - Mention the user
* `{username}` - Username

#### CUSTOM_CAPTION

* `{filename}` - file name of the Document
* `{previouscaption}` - Original Caption

#### CUSTOM_STATS

* `{uptime}` - Bot Uptime

## 𝐶𝑜𝑚𝑚𝑎𝑛𝑑𝑠

```
/start - start the bot or get posts
/batch - create link for more than one posts
/genlink - create link for one post
/users - view bot statistics
/broadcast - broadcast any messages to bot users
/stats - checking your bot uptime
```

### 💬 Support
Join Our [Telegram Group](https://www.telegram.dog/ultroidofficial_chat) For Support/Assistance And Our [Channel](https://www.telegram.dog/ultroid_official) For Updates.   
   
Report Bugs, Give Feature Requests There..   

### 🎉 Credits

- Thanks to ultroidxTeam for Modified this repo
- Thanks to Dan for his awesome library. [Libary](https://github.com/pyrogram/pyrogram)
Our support group members.

### 📝 License

GNU GPLv3 [![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl-3.0.en.html) 

[FILE-SHARING-BOT](https://github.com/7thofficial/File-Sharing-Bot/) is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 

   **Star this Repo if you Liked it ⭐⭐⭐**

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

