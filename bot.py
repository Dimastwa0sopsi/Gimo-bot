import telebot
import requests
from io import BytesIO
import os
from flask import Flask, request

# Безопасно: токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY")

QWEN_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
IMAGE_URL = "https://image.pollinations.ai/prompt/"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши вопрос или 'нарисуй [описание]'")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text
    
    if text.lower().startswith("нарисуй"):
        prompt = text[7:].strip()
        url = f"{IMAGE_URL}{requests.utils.quote(prompt)}?width=1024&height=1024"
        try:
            img = requests.get(url, timeout=30).content
            bot.send_photo(message.chat.id, BytesIO(img), caption=f"Результат: {prompt}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при создании картинки: {e}")
    else:
        headers = {"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": text}]
        }
        try:
            resp = requests.post(QWEN_URL, json=data, headers=headers, timeout=30).json()
            answer = resp["choices"][0]["message"]["content"]
            bot.send_message(message.chat.id, answer)
        except Exception as e:
            bot.send_message(message.chat.id, "Ой, что-то пошло не так. Попробуй позже.")

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://ТВОЙ-СЕРВИС.onrender.com/" + TELEGRAM_TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
