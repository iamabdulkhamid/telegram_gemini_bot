import telebot
import google.generativeai as genai
import os
from flask import Flask, request
import threading

# Flask server yaratamiz
app = Flask(__name__)

# Telegram bot tokeni
TELEGRAM_TOKEN = os.getenv("Telegramtoken")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Google Gemini API kaliti
GENAI_API_KEY = os.getenv("GENAI")
genai.configure(api_key=GENAI_API_KEY)

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

# Flask server (Render uni faol ushlab turish uchun kerak)
@app.route('/')
def home():
    return "Bot is running!"

# Telegram botni fon rejimida ishga tushirish
def start_bot():
    bot.infinity_polling()

# Gunicorn uchun WSGI ilova
if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
