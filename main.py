import telebot
import google.generativeai as genai
import os
from flask import Flask, request

# Flask server yaratamiz
app = Flask(__name__)

# Telegram bot tokeni
TELEGRAM_TOKEN = os.getenv("Telegramtoken")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Google Gemini API kaliti
GENAI_API_KEY = os.getenv("GENAI")
genai.configure(api_key=GENAI_API_KEY)

# Webhook URL
WEBHOOK_URL = "https://telegram-gemini-bot-vrp8.onrender.com/" + TELEGRAM_TOKEN

# Modelni yuklash
model = genai.GenerativeModel("gemini-2.0-flash")

# Xabarlarni qayta ishlash
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = get_gemini_response(message.text)
    bot.send_message(message.chat.id, response)

# Gemini'dan javob olish funksiyasi
def get_gemini_response(user_input):
    try:
        completion = model.generate_content(
            user_input,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1500
            )
        )
        return completion.text if hasattr(completion, "text") else "Xato: javob topilmadi."
    except Exception as e:
        return f"Xato yuz berdi: {e}"

# Webhookni sozlash
@app.route("/" + TELEGRAM_TOKEN, methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

@app.route('/')
def home():
    return "Bot is running with webhook!"

if __name__ == "__main__":
    # Eski webhookni tozalaymiz va yangisini o‘rnatamiz
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    # Flask serverni ishga tushiramiz
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
