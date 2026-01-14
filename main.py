import os
from flask import Flask, request
import telebot
from pymongo import MongoClient

# ================= ENV VARIABLES =================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

OWNER_ID = int(os.environ.get("OWNER_ID"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))

SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP")
SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL")

BOT_NAME = "AYESHA CHATBOT"
BOT_OWNER_NAME = "OZIXCEO"

# =================================================

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

mongo = MongoClient(MONGO_URL)
db = mongo["ayesha_bot"]
users = db["users"]

# ================= START COMMAND =================

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    username = user.username if user.username else "NoUsername"

    text = (
        f"Hello {user.first_name}! 😊<br><br>"
        "How are you?<br><br>"
        f"I am {BOT_NAME}<br>"
        f'Owner: <a href="tg://user?id={OWNER_ID}">{BOT_OWNER_NAME}</a> 💖'
    )

    bot.send_message(message.chat.id, text)

    # Save user
    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "username": username,
            "name": user.first_name
        }},
        upsert=True
    )

    # Log channel
    log = (
        "BOT STARTED<br><br>"
        f"Name: {user.first_name}<br>"
        f"User ID: {user.id}<br>"
        f"Username: @{username}"
    )
    bot.send_message(LOG_CHANNEL_ID, log)

# ============ BOT ADDED TO GROUP LOG ==============

@bot.my_chat_member_handler()
def added_to_group(update):
    chat = update.chat
    if chat.type in ["group", "supergroup"]:
        log = (
            "BOT ADDED TO GROUP<br><br>"
            f"Group Name: {chat.title}<br>"
            f"Group ID: {chat.id}"
        )
        bot.send_message(LOG_CHANNEL_ID, log)

# ============ NEW MEMBER WELCOME ==================

@bot.message_handler(content_types=["new_chat_members"])
def welcome(message):
    for member in message.new_chat_members:
        text = (
            f"Hello {member.first_name} 👋<br><br>"
            "Welcome to our group 😊<br>"
            "Stay active and enjoy ❤️<br><br>"
            f"User ID: {member.id}<br>"
            f'Group Owner: <a href="tg://user?id={OWNER_ID}">OWNER</a>'
        )
        bot.send_message(message.chat.id, text)

# ================= BROADCAST =====================

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        return

    msg = message.text.replace("/broadcast", "").strip()
    if not msg:
        bot.send_message(message.chat.id, "Message missing")
        return

    sent = 0
    for user in users.find():
        try:
            bot.send_message(user["user_id"], msg)
            sent += 1
        except:
            pass

    bot.send_message(message.chat.id, f"Broadcast sent to {sent} users")

# ================= SUPPORT =======================

@bot.message_handler(commands=["support"])
def support(message):
    text = (
        "SUPPORT<br><br>"
        f"Group: {SUPPORT_GROUP}<br>"
        f"Channel: {SUPPORT_CHANNEL}<br>"
        f'Owner: <a href="tg://user?id={OWNER_ID}">{BOT_OWNER_NAME}</a>'
    )
    bot.send_message(message.chat.id, text)

# ================= WEBHOOK =======================

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "AYESHA CHATBOT IS RUNNING"

# ================= RUN SERVER ====================

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    )

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
