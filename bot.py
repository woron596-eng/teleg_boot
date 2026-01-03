import telebot
import time
import logging
import os
from flask import Flask, request
import sys
import warnings
import requests

# Імпортуємо модулі
import config
import menu
import handlers

# Приховуємо попередження Flask
warnings.filterwarnings("ignore", message=".*development server.*")

# Створюємо бота
bot = telebot.TeleBot(config.TOKEN)

print("=" * 60)
print("🤖 БОТ ДЛЯ РЕМОНТУ АКУМУЛЯТОРІВ")
print(f"✅ Токен: {config.TOKEN[:10]}...")
print(f"✅ Канал: {config.CHANNEL_ID}")
print(f"✅ Режим: WEBHOOK")
print(f"✅ Webhook URL: {config.WEBHOOK_URL}")
print("=" * 60)

# Flask для Render
app = Flask(__name__)

# Приховуємо деталі Flask у логах
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ---------- ФУНКЦІЯ ДЛЯ ПУБЛІКАЦІЇ В КАНАЛ ----------
def post_to_channel():
    """Публікація поста в канал при запуску бота"""
    try:
        bot.send_message(
            config.CHANNEL_ID,
            "🚀 Бот для ремонту акумуляторів запущений!\n\n"
            "📱 Оберіть опцію нижче:",
            reply_markup=menu.create_channel_main_keyboard()
        )
        logger.info("✅ Пост успішно опубліковано в канал")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка публікації в канал: {e}")
        return False

# ---------- РЕЄСТРАЦІЯ ОБРОБНИКІВ ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start_wrapper(message):
    handlers.handle_start(bot, message)

@bot.message_handler(func=lambda message: True)
def handle_messages_wrapper(message):
    handlers.handle_messages(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Тут можна додати обробку callback-ів з menu.py
        # Наприклад, імпортувати функції обробки з окремого модуля
        
        bot.answer_callback_query(call.id)
    
    except Exception as e:
        logger.error(f"Error in callback: {e}")

# ---------- FLASK ЕНДПОІНТИ ----------
@app.route('/')
def home():
    return "🤖 Бот працює! Telegram: @tester_avto"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.route(f'/{config.TOKEN}', methods=['POST'])
def webhook():
    """Endpoint для отримання оновлень від Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# ---------- ГОЛОВНИЙ КОД ----------
if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 10000))
        
        logger.info(f"🚀 Запуск бота на Render")
        logger.info(f"🌐 Порт: {port}")
        logger.info(f"🔗 Webhook URL: {config.WEBHOOK_URL}")
        
        # Видаляємо старий webhook
        try:
            bot.remove_webhook()
            time.sleep(1)
        except:
            pass
        
        # Налаштовуємо новий webhook
        if config.WEBHOOK_URL:
            webhook_url = f"{config.WEBHOOK_URL}/{config.TOKEN}"
            try:
                bot.set_webhook(url=webhook_url, drop_pending_updates=True)
                logger.info(f"✅ Webhook налаштовано: {webhook_url}")
            except Exception as e:
                logger.error(f"⚠️ Помилка налаштування webhook: {e}")
        else:
            logger.error("❌ WEBHOOK_URL не встановлено! Бот не працюватиме.")
        
        # Публікуємо пост в канал при запуску
        time.sleep(2)  # Чекаємо трохи перед публікацією
        post_to_channel()
        
        # Запускаємо Flask
        logger.info(f"🌐 Запуск Flask сервера на порту {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    
    except Exception as e:
        logger.error(f"💥 Критична помилка: {e}")
        sys.exit(1)
