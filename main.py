import telebot
import google.generativeai as genai
import os
from flask import Flask, request

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

# Webhook uchun endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Webhookni sozlash
@app.route('/')
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    return "Webhook o‘rnatildi!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
