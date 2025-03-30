import os
import telebot
from flask import Flask, request
import google.generativeai as genai

# Flask server yaratamiz
app = Flask(__name__)

# Telegram bot tokeni
TELEGRAM_TOKEN = os.getenv("Telegramtoken")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Render yoki boshqa serverdagi to‘g‘ri URL

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Google Gemini API kaliti
GENAI_API_KEY = os.getenv("GENAI")
genai.configure(api_key=GENAI_API_KEY)

# Modelni yuklash
model = genai.GenerativeModel("gemini-2.0-flash")


# Foydalanuvchi yozgan xabarni qabul qilish
@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_text(message):
    response = get_gemini_response(message.text)
    bot.send_message(message.chat.id, response)


# Foydalanuvchi rasm yuborganda uni qabul qilish
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    file_id = message.photo[-1].file_id  # Eng katta o'lchamdagi rasmni tanlaymiz
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
    
    # Gemini API bilan ishlash (tasvirni generatsiya qilish yoki tahlil qilish uchun)
    try:
        response = model.generate_content(["Tasvirni tavsiflang:", file_url])
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")


# Webhook uchun endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# Webhookni sozlash
@app.route("/")
def home():
    return "Bot is running with webhook!", 200


if __name__ == "__main__":
    # Eski webhookni tozalaymiz va yangisini o‘rnatamiz
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    # Flask serverni ishga tushiramiz
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
