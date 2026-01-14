import telebot
from pymongo import MongoClient
from telebot.types import ChatMemberUpdated
import os

# ================== ENV CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL")

BOT_NAME = "AYESHA CHATBOT"
BOT_OWNER = "OZIXCEO"

# =================================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
mongo = MongoClient(MONGO_URL)
db = mongo["ayesha_bot"]
users = db["users"]

# ================= START =========================

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    text = f"""
✨ *Hello {user.first_name}!* 😊  
How are you?

🤖 I am *{BOT_NAME}*  
👑 Owner: *{BOT_OWNER}*

Welcome 💖
"""
    bot.send_message(message.chat.id, text)

    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "username": user.username,
            "name": user.first_name
        }},
        upsert=True
    )

    log = f"""
📥 *BOT START*

👤 Name: {user.first_name}
🆔 ID: `{user.id}`
🔗 Username: @{user.username}
"""
    bot.send_message(LOG_CHANNEL_ID, log)

# ================= BOT ADDED TO GROUP ============

@bot.my_chat_member_handler()
def group_log(update: ChatMemberUpdated):
    chat = update.chat
    if chat.type in ["group", "supergroup"]:
        log = f"""
➕ *BOT ADDED*

📛 Group: {chat.title}
🆔 Group ID: `{chat.id}`
"""
        bot.send_message(LOG_CHANNEL_ID, log)

# ================= NEW MEMBER ====================

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for member in message.new_chat_members:
        text = f"""
👋 *Hello {member.first_name}!* 💖  

Welcome to our GC 😊  
Stay active & enjoy 🎉

🆔 Your ID: `{member.id}`
👑 Group Owner: `{OWNER_ID}`
"""
        bot.send_message(message.chat.id, text)

# ================= BROADCAST =====================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        return

    msg = message.text.replace("/broadcast", "").strip()
    if not msg:
        bot.reply_to(message, "❌ Message missing")
        return

    success = 0
    for user in users.find():
        try:
            bot.send_message(user["user_id"], msg)
            success += 1
        except:
            pass

    bot.reply_to(message, f"✅ Broadcast sent to {success} users")

# ================= SUPPORT =======================

@bot.message_handler(commands=['support'])
def support(message):
    text = f"""
🆘 *Support Center*

👥 Group: {SUPPORT_GROUP}
📢 Channel: {SUPPORT_CHANNEL}
👑 Owner ID: `{OWNER_ID}`
"""
    bot.send_message(message.chat.id, text)

# ================= RUN ===========================

print("🤖 AYESHA CHATBOT IS LIVE")
bot.infinity_polling()
