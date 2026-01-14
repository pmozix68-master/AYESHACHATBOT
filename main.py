import os
from flask import Flask, request
import telebot
from pymongo import MongoClient

# ============== ENV VARIABLES =================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
OWNER_ID = int(os.environ.get("OWNER_ID"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))

SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL")

BOT_NAME = "AYESHA CHATBOT"
BOT_OWNER = "OZIXCEO"

# ==============================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

mongo = MongoClient(MONGO_URL)
db = mongo["ayesha_bot"]
users = db["users"]

# ================= START =======================

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    username = user.username if user.username else "NoUsername"

    text = (
        f"✨ Hello {user.first_name}! 😊\n\n"
        f"How are you?\n\n"
        f"I am {BOT_NAME}\n"
        f"Owner: {BOT_OWNER} 💖"
    )

    bot.send_message(message.chat.id, text)

    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "username": username,
            "name": user.first_name
        }},
        upsert=True
    )

    log = (
        "📥 BOT STARTED\n\n"
        f"Name: {user.first_name}\n"
        f"User ID: {user.id}\n"
        f"Username: @{username}"
    )
    bot.send_message(LOG_CHANNEL_ID, log)

# ================= GROUP ADD LOG ================

@bot.my_chat_member_handler()
def bot_added(update):
    chat = update.chat
    if chat.type in ["group", "supergroup"]:
        log = (
            "➕ BOT ADDED TO GROUP\n\n"
            f"Group Name: {chat.title}\n"
            f"Group ID: {chat.id}"
        )
        bot.send_message(LOG_CHANNEL_ID, log)

# ================= NEW MEMBER ===================

@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for member in message.new_chat_members:
        text = (
            f"👋 Hello {member.first_name}!\n\n"
            "Welcome to our group 😊\n"
            "Stay active and enjoy 💫\n\n"
            f"User ID: {member.id}\n"
            f"Group Owner ID: {OWNER_ID}"
        )
        bot.send_message(message.chat.id, text)

# ================= BROADCAST ====================

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        return

    msg = message.text.replace("/broadcast", "").strip()
    if not msg:
        bot.send_message(message.chat.id, "❌ Message missing")
        return

    sent = 0
    for user in users.find():
        try:
            bot.send_message(user["user_id"], msg)
            sent += 1
        except:
            pass

    bot.send_message(message.chat.id, f"✅ Broadcast sent to {sent} users")

# ================= SUPPORT ======================

@bot.message_handler(commands=["support"])
def support(message):
    text = (
        "🆘 SUPPORT\n\n"
        f"Group: {SUPPORT_GROUP}\n"
        f"Channel: {SUPPORT_CHANNEL}\n"
        f"Owner ID: {OWNER_ID}"
    )
    bot.send_message(message.chat.id, text)

# ================= WEBHOOK ======================

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.stream.read().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "AYESHA CHATBOT IS RUNNING"

# ================= START SERVER =================

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    )

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
