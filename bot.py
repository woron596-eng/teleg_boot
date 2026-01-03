import telebot
import time
import logging
import os
from flask import Flask, request
import sys
import warnings
import requests
import threading

# Імпортуємо модулі
import config
import menu

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
    time.sleep(5)  # Чекаємо, поки webhook налаштується
    try:
        # Використовуємо API напряму для відправки в канал
        url = f"https://api.telegram.org/bot{config.TOKEN}/sendMessage"
        
        # Текст повідомлення
        message_text = (
            "🚀 *Бот для ремонту акумуляторів запущений!*\n\n"
            "📱 *Доступні опції:*\n"
            "• Ремонт акумуляторів Дніпро-M\n"
            "• Калькулятор розрахунку вартості\n"
            "• Інформація про гарантію\n"
            "• Умови відправки та оплати\n\n"
            "💬 *Щоб почати:* напишіть боту @tester_avto_bot /start"
        )
        
        # Створюємо inline клавіатуру
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Дніпро-M", "callback_data": "brand_dnipro"},
                    {"text": "Калькулятор", "callback_data": "show_calculator"}
                ],
                [
                    {"text": "Гарантія", "callback_data": "warranty"},
                    {"text": "Відправка та оплата", "callback_data": "shipping_payment"}
                ]
            ]
        }
        
        data = {
            "chat_id": config.CHANNEL_ID,
            "text": message_text,
            "parse_mode": "Markdown",
            "reply_markup": inline_keyboard
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info("✅ Пост успішно опубліковано в канал")
                return True
            else:
                logger.error(f"❌ Помилка API: {result}")
        else:
            logger.error(f"❌ Помилка HTTP: {response.status_code}")
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Помилка публікації в канал: {e}")
        return False

# ---------- АЛЬТЕРНАТИВНА ФУНКЦІЯ ЧЕРЕЗ БОТА ----------
def post_with_bot():
    """Альтернативна функція публікації через об'єкт бота"""
    try:
        # Чекаємо, щоб бот ініціалізувався
        time.sleep(3)
        
        bot.send_message(
            config.CHANNEL_ID,
            "🚀 *Бот для ремонту акумуляторів запущений!*\n\n"
            "📱 *Доступні опції:*\n"
            "• Ремонт акумуляторів Дніпро-M\n"
            "• Калькулятор розрахунку вартості\n"
            "• Інформація про гарантію\n"
            "• Умови відправки та оплати\n\n"
            "💬 *Щоб почати:* напишіть боту @tester_avto_bot /start",
            parse_mode="Markdown",
            reply_markup=menu.create_channel_main_keyboard()
        )
        logger.info("✅ Пост успішно опубліковано в канал")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка публікації через бота: {e}")
        return False

# ---------- РЕЄСТРАЦІЯ ОБРОБНИКІВ ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    try:
        bot.send_message(
            message.chat.id,
            "🔋 *Ремонт акумуляторів*\n\n"
            "Оберіть опцію:",
            reply_markup=menu.create_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Головне меню
        if text == "Дніпро-M":
            menu.user_selection[user_id] = {'brand': 'Дніпро-M'}
            bot.send_message(
                chat_id,
                "🔋 *Ремонт акумуляторів*\n"
                "Бренд: *Дніпро-M*\n\n"
                "Оберіть модель АКБ:",
                reply_markup=menu.create_models_keyboard(),
                parse_mode="Markdown"
            )
        
        elif text == "Калькулятор":
            menu.user_calculator[user_id] = {'step': 'format'}
            bot.send_message(
                chat_id,
                "🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
                "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
                "*Оберіть формат елементів:*",
                reply_markup=menu.create_calculator_format_keyboard(),
                parse_mode="Markdown"
            )
        
        elif text == "Гарантія":
            warranty_text = (
                "📜 *ГАРАНТІЯ:*\n\n"
                "✅ На всі відремонтовані акумулятори надається гарантія:\n"
                "• 3 місяці на елементи акумулятора\n"
                "• 6 місяців на пайку та збірку\n"
                "• Гарантія діє з моменту отримання\n"
                "• У разі виникнення проблем - безкоштовний ремонт або заміна"
            )
            bot.send_message(chat_id, warranty_text, 
                           reply_markup=menu.create_main_keyboard(),
                           parse_mode="Markdown")
        
        elif text == "Відправка та оплата":
            shipping_text = (
                "🚚 *ВІДПРАВКА ТА ОПЛАТА:*\n\n"
                "📦 *Варіанти відправки:*\n"
                "• Нова Пошта - 1-3 дні\n"
                "• Доставка по м.Надвірна (Безкоштовна)\n\n"
                "💳 *Оплата на карту перед відправкою:*\n"
                "• Стандартний ремонт - 1-3 дні"
            )
            bot.send_message(chat_id, shipping_text, 
                           reply_markup=menu.create_main_keyboard(),
                           parse_mode="Markdown")
        
        # Обробка кнопки "Назад"
        elif text == "◀️ Назад":
            bot.send_message(
                chat_id,
                "🔋 *Ремонт акумуляторів*\n\n"
                "Оберіть опцію:",
                reply_markup=menu.create_main_keyboard(),
                parse_mode="Markdown"
            )
        
        # Додайте інші обробники з вашого коду тут...
        # (це скорочений приклад)
        
        else:
            bot.send_message(
                chat_id,
                "🔋 *Ремонт акумуляторів*\n\n"
                "Оберіть опцію:",
                reply_markup=menu.create_main_keyboard(),
                parse_mode="Markdown"
            )
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        if call.data == "brand_dnipro":
            try:
                bot.edit_message_text(
                    "🔋 *Ремонт акумуляторів*\n"
                    "Бренд: *Дніпро-M*\n\n"
                    "Оберіть модель АКБ:",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=menu.create_channel_models_keyboard(),
                    parse_mode="Markdown"
                )
            except:
                # Якщо не вдалося відредагувати
                bot.send_message(
                    chat_id,
                    "🔋 *Ремонт акумуляторів*\n"
                    "Бренд: *Дніпро-M*\n\n"
                    "Оберіть модель АКБ:",
                    reply_markup=menu.create_channel_models_keyboard(),
                    parse_mode="Markdown"
                )
        
        elif call.data == "show_calculator":
            try:
                bot.edit_message_text(
                    "🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
                    "Оберіть формат елементів:",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=menu.create_channel_calculator_format_keyboard(),
                    parse_mode="Markdown"
                )
            except:
                bot.send_message(
                    chat_id,
                    "🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
                    "Оберіть формат елементів:",
                    reply_markup=menu.create_channel_calculator_format_keyboard(),
                    parse_mode="Markdown"
                )
        
        elif call.data == "warranty":
            warranty_text = (
                "📜 *ГАРАНТІЯ:*\n\n"
                "❌ Гарантія на БМС не надається (Дніпро-М)\n"
                "✅ На всі відремонтовані акумулятори:\n"
                "• 6 місяців на елементи\n"
                "• 6 місяців на зварку та збірку\n"
                "• Безкоштовний ремонт при гарантійному випадку"
            )
            try:
                bot.edit_message_text(
                    warranty_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=menu.create_channel_main_keyboard(),
                    parse_mode="Markdown"
                )
            except:
                bot.send_message(
                    chat_id,
                    warranty_text,
                    reply_markup=menu.create_channel_main_keyboard(),
                    parse_mode="Markdown"
                )
        
        elif call.data == "back_to_main":
            try:
                bot.edit_message_text(
                    "🔋 *Ремонт акумуляторів*\n\n"
                    "Оберіть опцію:",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=menu.create_channel_main_keyboard(),
                    parse_mode="Markdown"
                )
            except:
                bot.send_message(
                    chat_id,
                    "🔋 *Ремонт акумуляторів*\n\n"
                    "Оберіть опцію:",
                    reply_markup=menu.create_channel_main_keyboard(),
                    parse_mode="Markdown"
                )
        
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

@app.route('/post')
def manual_post():
    """Ручне відправлення поста в канал"""
    if post_to_channel():
        return "✅ Пост опубліковано в канал"
    else:
        return "❌ Не вдалося опублікувати пост"

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
        
        # Запускаємо публікацію в канал в окремому потоці
        def delayed_post():
            time.sleep(8)  # Чекаємо, поки все налаштується
            logger.info("📢 Спроба публікації поста в канал...")
            if post_with_bot():  # Спершу пробуємо через бота
                logger.info("✅ Успішна публікація через бота")
            else:
                logger.info("🔄 Спроба через API...")
                post_to_channel()  # Якщо не вийшло, пробуємо через API
        
        post_thread = threading.Thread(target=delayed_post, daemon=True)
        post_thread.start()
        
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
