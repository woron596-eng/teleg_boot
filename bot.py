import telebot
from telebot import types
import time
import logging
import os
from flask import Flask, request
import threading
import requests
import sys
import warnings
import json
from functools import lru_cache

# ==================== КОНФІГУРАЦІЯ ====================
TOKEN = "8252548275:AAF0qYbEZCoBPEN6gNHx2kkYi9gHoUPNKrA"
CHANNEL_ID = "@tester_avto"

# Приховуємо попередження Flask
warnings.filterwarnings("ignore", message=".*development server.*")

# Налаштування для Webhook
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', os.environ.get('WEBHOOK_URL', ''))

# ШВИДКИЙ СТАРТ: Завантажуємо дані в пам'ять при старті
# ==================== ШВИДКОЗАВАНТАЖУВАНІ ДАНІ ====================
_CALCULATOR_DATA = {
    "18650": {
        "element_capacity": "3000mAh",
        "prices": {
            "2шт": {"Ampace JP30 36А": 700, "EVE 30P 20A": 550, "DMEGC 30P 20A": 550},
            "3шт": {"Ampace JP30 36А": 850, "EVE 30P 20A": 700, "DMEGC 30P 20A": 700},
            "4шт": {"Ampace JP30 36А": 1100, "EVE 30P 20A": 800, "DMEGC 30P 20A": 800},
            "5шт": {"Ampace JP30 36А": 1250, "EVE 30P 20A": 900, "DMEGC 30P 20A": 900},
            "6шт": {"Ampace JP30 36А": 1400, "EVE 30P 20A": 1150, "DMEGC 30P 20A": 1150},
            "10шт": {"Ampace JP30 36А": 2000, "EVE 30P 20A": 1600, "DMEGC 30P 20A": 1600},
            "12шт": {"Ampace JP30 36А": 2450, "EVE 30P 20A": 1800, "DMEGC 30P 20A": 1800},
            "15шт": {"Ampace JP30 36А": 2900, "EVE 30P 20A": 2100, "DMEGC 30P 20A": 2100},
            "20шт": {"Ampace JP30 36А": 3800, "EVE 30P 20A": 2800, "DMEGC 30P 20A": 2800}
        },
        "total_capacity": {
            "2шт": "3Ah", "3шт": "3Ah", "4шт": "3Ah", "5шт": "3Ah", "6шт": "3Ah",
            "10шт": "6Ah", "12шт": "6Ah", "15шт": "9Ah", "20шт": "12Ah"
        }
    },
    "21700": {
        "element_capacity": "4000mAh",
        "prices": {
            "2шт": {"Ampace JP40 70А": 700},
            "3шт": {"Ampace JP40 70А": 950},
            "4шт": {"Ampace JP40 70А": 1100},
            "5шт": {"Ampace JP40 70А": 1350},
            "6шт": {"Ampace JP40 70А": 1450},
            "10шт": {"Ampace JP40 70А": 2200},
            "12шт": {"Ampace JP40 70А": 2500},
            "15шт": {"Ampace JP40 70А": 2800},
            "20шт": {"Ampace JP40 70А": 3700}
        },
        "total_capacity": {
            "2шт": "4Ah", "3шт": "4Ah", "4шт": "4Ah", "5шт": "4Ah", "6шт": "4Ah",
            "10шт": "8Ah", "12шт": "8Ah", "15шт": "12Ah", "20шт": "16Ah"
        }
    }
}

_MODELS_STRUCTURE = {
    "BP‑122 12V / 2.0Ah": {
        "type": "12V блок", "capacity": "3000mAh", "voltage": "12V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 850),
            ("EVE 30P 3000mAh 20A", "3000mAh", 700),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 700),
        ]
    },
    "BP‑125 12V / 4.0Ah": {
        "type": "12V блок", "capacity": "6000mAh", "voltage": "12V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 1500),
            ("EVE 30P 3000mAh 20A", "3000mAh", 1200),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 1200),
        ]
    },
    "BP‑220 (2 Ah)": {
        "type": "18650", "capacity": "3000mAh", "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 1250),
            ("EVE 30P 3000mAh 20A", "3000mAh", 900),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 900),
        ]
    },
    "BP‑240 (4 Ah)": {
        "type": "18650", "capacity": "6000mAh", "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 2000),
            ("EVE 30P 3000mAh 20A", "3000mAh", 1600),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 1600),
        ]
    },
    "BP‑260 (6 Ah)": {
        "type": "18650", "capacity": "9000mAh", "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 2900),
            ("EVE 30P 3000mAh 20A", "3000mAh", 2100),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 2100),
        ]
    },
    "BP‑240N (4 Ah)": {
        "type": "21700", "capacity": "4000mAh", "voltage": "20V",
        "batteries": [
            ("Ampace JP40 70А", "4000mAh", 1350),
        ]
    },
    "BP‑280N (8 Ah)": {
        "type": "21700", "capacity": "8000mAh", "voltage": "20V",
        "batteries": [
            ("Ampace JP40 70А", "4000mAh", 2200),
        ]
    }
}

print("=" * 50)
print("🤖 БОТ ДЛЯ РЕМОНТУ АКУМУЛЯТОРІВ")
print(f"✅ Токен: {TOKEN[:10]}...")
print(f"✅ Канал: {CHANNEL_ID}")
print(f"✅ Режим: WEBHOOK")
if WEBHOOK_URL:
    print(f"✅ Webhook URL: {WEBHOOK_URL}")
else:
    print("⚠️ Увага: WEBHOOK_URL не встановлено!")
print("=" * 50)

# ШВИДКИЙ СТАРТ: Ініціалізація бота
bot = telebot.TeleBot(TOKEN, threaded=False)  # threaded=False для кращої сумісності з Flask
app = Flask(__name__)

# Логування
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Глобальні змінні для збереження стану (оптимізовано)
user_selection = {}
user_calculator = {}

# ==================== КЕШУВАННЯ КЛАВІАТУР ====================
@lru_cache(maxsize=10)
def get_main_keyboard():
    """Кешована головна клавіатура"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Дніпро-M", "Калькулятор", "Гарантія", "Відправка та оплата")
    return keyboard

@lru_cache(maxsize=10)
def get_models_keyboard():
    """Кешована клавіатура моделей"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = list(_MODELS_STRUCTURE.keys())
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    keyboard.add("◀️ Назад")
    return keyboard

# Кеш для інших клавіатур
_keyboard_cache = {}

def get_cached_keyboard(cache_key, create_func, *args):
    """Універсальна функція кешування клавіатур"""
    if cache_key not in _keyboard_cache:
        _keyboard_cache[cache_key] = create_func(*args)
    return _keyboard_cache[cache_key]

# ==================== ОПТИМІЗОВАНІ ФУНКЦІЇ КЛАВІАТУР ====================
def create_battery_type_keyboard_fast(model_key):
    """Швидке створення клавіатури типів акумуляторів"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    batteries = _MODELS_STRUCTURE[model_key]["batteries"]
    for battery_name, _, battery_price in batteries:
        keyboard.add(f"{battery_name} - {battery_price} грн")
    keyboard.add("◀️ Назад до моделей")
    return keyboard

def create_calculator_format_keyboard_fast():
    """Швидка клавіатура формату калькулятора"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("18650", "21700")
    keyboard.add("◀️ Назад")
    return keyboard

# ==================== ОБРОБНИКИ З ШВИДКОЮ ВІДПОВІДДЮ ====================
@bot.message_handler(commands=['start', 'help'])
def handle_start_fast(message):
    """Оптимізований обробник старту"""
    try:
        bot.send_message(
            message.chat.id,
            "Ремонт акумуляторів\n\nОберіть опцію:",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Start error: {e}")

@bot.message_handler(func=lambda message: message.text == "Дніпро-M")
def handle_dnipro_fast(message):
    """Швидкий обробник для Дніпро-M"""
    user_selection[message.from_user.id] = {'brand': 'Дніпро-M'}
    bot.send_message(
        message.chat.id,
        "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
        reply_markup=get_models_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "Калькулятор")
def handle_calculator_fast(message):
    """Швидкий обробник калькулятора"""
    user_calculator[message.from_user.id] = {'step': 'format'}
    bot.send_message(
        message.chat.id,
        "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
        "Розберіть акумулятор, порахуйте кількість елементів:\n\n"
        "**Оберіть формат елементів:**",
        reply_markup=create_calculator_format_keyboard_fast(),
        parse_mode="Markdown"
    )

# ==================== КЕП-ЕЛАЙВ СИСТЕМА ====================
def keep_alive():
    """Підтримка активності бота на Render"""
    if not WEBHOOK_URL:
        return
    
    while True:
        try:
            time.sleep(300)  # Кожні 5 хвилин
            requests.get(f"{WEBHOOK_URL}/health", timeout=5)
            logger.debug("Keep-alive ping sent")
        except Exception as e:
            logger.debug(f"Keep-alive error: {e}")
            time.sleep(60)  # Чекаємо довше при помилці

# ==================== OPTIMIZED FLASK ENDPOINTS ====================
@app.route('/')
def home_light():
    """Мінімальна головна сторінка"""
    return "🤖 Бот працює!", 200

@app.route('/health')
def health_light():
    """Швидкий health check"""
    return json.dumps({"status": "ok", "time": time.time()}), 200, {'Content-Type': 'application/json'}

@app.route('/ping')
def ping_light():
    """Найшвидший ping endpoint"""
    return "pong", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_fast():
    """Оптимізований webhook endpoint"""
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data(as_text=True)
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return 'Error', 500
    return 'Forbidden', 403

# ==================== ШВИДКИЙ ЗАПУСК ====================
def setup_webhook_async():
    """Асинхронне налаштування webhook (не блокує старт)"""
    time.sleep(2)  # Чекаємо запуск Flask
    if WEBHOOK_URL:
        try:
            webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url, drop_pending_updates=True)
            logger.info(f"✅ Webhook: {webhook_url[:50]}...")
        except Exception as e:
            logger.error(f"Webhook setup error: {e}")

if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 10000))
        
        logger.info(f"🚀 Швидкий запуск бота")
        logger.info(f"🌐 Порт: {port}")
        
        # Запускаємо keep-alive в окремому потоці
        keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        keep_alive_thread.start()
        
        # Запускаємо webhook setup в окремому потоці
        webhook_thread = threading.Thread(target=setup_webhook_async, daemon=True)
        webhook_thread.start()
        
        # ШВИДКИЙ ЗАПУСК FLASK
        from waitress import serve  # Використовуємо waitress замість dev server
        
        logger.info("🌐 Запуск сервера (Waitress)...")
        serve(app, host='0.0.0.0', port=port, threads=4)
        
    except ImportError:
        # Якщо waitress не встановлено, використовуємо стандартний Flask
        logger.warning("⚠️ Waitress не знайдено, використовуємо Flask dev server")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"💥 Помилка запуску: {e}")
        sys.exit(1)
