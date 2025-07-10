import asyncio, time


async def extract_user(bot, message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    args = message.text.split()
    if len(args) > 1:
        target = args[1]
        if target.isdigit():
            return int(target)
        try:
            user = await bot.get_users(target)
            return user.id
        except:
            return None
    return None
    

async def send_premium_reminders(bot_instance, phdlust):
    while True:
        now = time.time()
        # Send reminder to active premium users
        premium_users = phdlust.find({"is_premium": True, "expiry_time": {"$gt": now}})
        for user in premium_users:
            user_id = user.get("user_id")
            expiry_time = user.get("expiry_time")
            days_left = max(int((expiry_time - now) / 86400), 0)
            try:
                await bot_instance.send_message(
                    user_id,
                    f"⚠️ Bas {days_left} din aur…"
                )
            except Exception as e:
                print(f"Failed to send message: {e}")
            await asyncio.sleep(0.5)  # Thoda delay, load kam karne ke liye
        # Send renewal message to users whose premium just expired and not notified
        expired_users = phdlust.find({
            "is_premium": True,
            "expiry_time": {"$lte": now},
            "notified_expired": {"$ne": True}
        })
        for user in expired_users:
            user_id = user.get("user_id")
            try:
                await bot_instance.send_message(
                    user_id,
                    "❌ Aapka premium khatam ho gaya hai! Renew karne ke liye /plan ya admin se sampark karein."
                )
                phdlust.update_one({"user_id": user_id}, {"$set": {"notified_expired": True}})
            except Exception as e:
                print(f"Failed to send renewal message: {e}")
            await asyncio.sleep(0.5)  # Thoda delay, load kam karne ke liye
        # Sleep until next day (24 hours)
        await asyncio.sleep(86400)

def start_premium_reminder_scheduler(bot_instance, phdlust):
    asyncio.create_task(send_premium_reminders(bot_instance, phdlust))
