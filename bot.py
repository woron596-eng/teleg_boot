import telebot
from telebot import types
import time
import logging
import os
from flask import Flask
import threading

# ----------------------------
# ГЛОБАЛЬНІ ЗМІННІ (щоб були доступні всюди)
TOKEN = None
CHANNEL_ID = None
bot = None

# НАЛАШТУВАННЯ ДЛЯ RENDER
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот для ремонту акумуляторів працює! Статус: Активний"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ----------------------------
# НАЛАШТУВАННЯ ЛОГУВАННЯ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------- ІНІЦІАЛІЗАЦІЯ ----------
def init_bot():
    """Ініціалізує бота зі змінних середовища"""
    global TOKEN, CHANNEL_ID, bot
    
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    CHANNEL_ID = os.environ.get('CHANNEL_ID', '@tester_avto')
    
    if not TOKEN:
        logger.error("❌ ПОМИЛКА: TELEGRAM_TOKEN не встановлено!")
        logger.error("📝 Встановіть змінну середовища TELEGRAM_TOKEN на Render.com")
        logger.info("⏸️ Бот запускається в режимі очікування...")
        # Створюємо фейкового бота для тесту
        bot = telebot.TeleBot("dummy_token")
        return False
    
    bot = telebot.TeleBot(TOKEN)
    logger.info("✅ Токен отримано успішно")
    return True

# ---------- ЦІНИ ДЛЯ КОЖНОГО ТИПУ АКУМУЛЯТОРА ----------
# ДЛЯ 18650 АКУМУЛЯТОРІВ
akb_18650_prices = {
    "Ampace JP30 3000mAh 36А": 200,
    "EVE 30P 3000mAh 20A": 180,
    "DMEGC 30P 3000mAh 20A": 170,
}

# ДЛЯ 21700 АКУМУЛЯТОРІВ
akb_21700_prices = {
    "Ampace JP40 70А": 300,
}

# ---------- СТРУКТУРА МОДЕЛЕЙ ----------
models_structure = {
    "BP‑220 (2 Ah)": {
        "type": "18650",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", 200),
            ("EVE 30P 3000mAh 20A", 180),
            ("DMEGC 30P 3000mAh 20A", 170),
        ]
    },
    "BP‑240 (4 Ah)": {
        "type": "18650", 
        "batteries": [
            ("Ampace JP30 3000mAh 36А", 200),
            ("EVE 30P 3000mAh 20A", 180),
            ("DMEGC 30P 3000mAh 20A", 170),
        ]
    },
    "BP‑260 (6 Ah)": {
        "type": "18650",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", 200),
            ("EVE 30P 3000mAh 20A", 180),
            ("DMEGC 30P 3000mAh 20A", 170),
        ]
    },
    "BP‑240N (4 Ah)": {
        "type": "21700",
        "batteries": [
            ("Ampace JP40 70А", 300),
        ]
    },
    "BP‑280N (8 Ah)": {
        "type": "21700",
        "batteries": [
            ("Ampace JP40 70А", 300),
        ]
    }
}

# Зберігаємо вибір користувачів
user_selection = {}

# ---------- ФУНКЦІЇ ДЛЯ КЛАВІАТУР ----------
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Дніпро-M", "Прайс")
    return keyboard

def create_models_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = list(models_structure.keys())
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    keyboard.add("Назад")
    return keyboard

def create_battery_type_keyboard(model_key):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    batteries = models_structure[model_key]["batteries"]
    for battery_name, battery_price in batteries:
        keyboard.add(f"{battery_name} - {battery_price} грн")
    keyboard.add("Назад до моделей")
    return keyboard

def create_count_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    numbers = [str(i) for i in range(1, 11)]
    keyboard.add(*numbers[:5])
    keyboard.add(*numbers[5:])
    keyboard.add("Назад до типів АКБ")
    return keyboard

def create_channel_main_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Дніпро-M", callback_data="brand_dnipro"),
        types.InlineKeyboardButton("Прайс", callback_data="show_price")
    )
    return keyboard

def create_channel_models_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for model in models_structure:
        buttons.append(types.InlineKeyboardButton(model, callback_data=f"model_{model}"))
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_main"))
    return keyboard

def create_channel_battery_keyboard(model_key):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    batteries = models_structure[model_key]["batteries"]
    for battery_name, battery_price in batteries:
        clean_name = battery_name.replace(" ", "_").replace(",", "")
        callback_data = f"battery_{model_key}_{clean_name}"
        button_text = f"{battery_name} - {battery_price} грн"
        keyboard.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_models"))
    return keyboard

def create_channel_count_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 11):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"count_{i}"))
    for i in range(0, len(buttons), 5):
        keyboard.add(*buttons[i:i+5])
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_batteries"))
    return keyboard

def find_battery_price(model_key, battery_name):
    batteries = models_structure[model_key]["batteries"]
    for name, price in batteries:
        if name == battery_name:
            return price
    return None

# ---------- ПУБЛІКАЦІЯ В КАНАЛ ----------
def post_to_channel_with_retry(max_retries=3, delay=5):
    if not TOKEN or TOKEN == "dummy_token":
        logger.warning("⏸️ Пропускаємо публікацію: токен не встановлено або фейковий")
        return False
        
    for attempt in range(max_retries):
        try:
            bot.send_message(
                CHANNEL_ID,
                "Ремонт акумуляторів\n\nОберіть бренд:",
                reply_markup=create_channel_main_keyboard()
            )
            logger.info(f"✅ Повідомлення опубліковано в канал {CHANNEL_ID}")
            return True
        except Exception as e:
            logger.warning(f"Спроба {attempt + 1}/{max_retries} не вдалася: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    logger.error(f"❌ Не вдалося опублікувати в канал після {max_retries} спроб")
    return False

# ---------- ОБРОБНИКИ ПОВІДОМЛЕНЬ ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    try:
        bot.send_message(
            message.chat.id,
            "Ремонт акумуляторів\n\nОберіть бренд:",
            reply_markup=create_main_keyboard()
        )
        logger.info(f"Користувач {message.from_user.id} запустив бота")
    except Exception as e:
        logger.error(f"Помилка в handle_start: {e}")

@bot.message_handler(commands=['status'])
def handle_status(message):
    try:
        bot.send_message(
            message.chat.id,
            "🤖 Бот працює нормально!\n"
            "🕒 Сервер час: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
            "📊 Користувачів в пам'яті: " + str(len(user_selection))
        )
    except Exception as e:
        logger.error(f"Помилка в handle_status: {e}")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text == "Дніпро-M":
            user_selection[user_id] = {'brand': 'Дніпро-M'}
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                reply_markup=create_models_keyboard()
            )
        
        elif text == "Прайс":
            price_text = "📋 ПРАЙС Дніпро-М (ціна за 1 елемент):\n\n"
            for model_name, model_data in models_structure.items():
                price_text += f"\n{model_name} ({model_data['type']}):\n"
                for battery_name, battery_price in model_data["batteries"]:
                    price_text += f"  • {battery_name} — {battery_price} грн\n"
            bot.send_message(chat_id, price_text, reply_markup=create_main_keyboard())
        
        elif text == "Назад":
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\n\nОберіть бренд:",
                reply_markup=create_main_keyboard()
            )
        
        elif text == "Назад до моделей":
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                reply_markup=create_models_keyboard()
            )
        
        elif text == "Назад до типів АКБ":
            if user_id in user_selection and 'model' in user_selection[user_id]:
                model = user_selection[user_id]['model']
                bot.send_message(
                    chat_id,
                    f"Ремонт акумуляторів\nМодель: {model}\n\nОберіть тип акумулятора:",
                    reply_markup=create_battery_type_keyboard(model)
                )
            else:
                bot.send_message(
                    chat_id,
                    "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                    reply_markup=create_models_keyboard()
                )
        
        elif text in models_structure:
            if user_id not in user_selection:
                user_selection[user_id] = {}
            user_selection[user_id]['model'] = text
            bot.send_message(
                chat_id,
                f"Ремонт акумуляторів\nМодель: {text}\nТип: {models_structure[text]['type']}\n\nОберіть тип акумулятора:",
                reply_markup=create_battery_type_keyboard(text)
            )
        
        elif " - " in text and " грн" in text:
            battery_name = text.split(" - ")[0].strip()
            if user_id in user_selection and 'model' in user_selection[user_id]:
                model_key = user_selection[user_id]['model']
                price = find_battery_price(model_key, battery_name)
                if price:
                    user_selection[user_id]['battery_type'] = battery_name
                    user_selection[user_id]['price_per_unit'] = price
                    bot.send_message(
                        chat_id,
                        f"Ремонт акумуляторів\nМодель: {model_key}\nТип АКБ: {battery_name}\nЦіна за 1: {price} грн\n\nОберіть кількість елементів:",
                        reply_markup=create_count_keyboard()
                    )
        
        elif text.isdigit() and 1 <= int(text) <= 10:
            if user_id in user_selection and 'battery_type' in user_selection[user_id]:
                count = int(text)
                model = user_selection[user_id]['model']
                battery_type = user_selection[user_id]['battery_type']
                price_per = user_selection[user_id]['price_per_unit']
                total = price_per * count
                bot.send_message(
                    chat_id,
                    f"🧾 ЗАМОВЛЕННЯ:\n\n🔋 Модель: {model}\n⚡ Тип АКБ: {battery_type}\n📦 Кількість: {count} елементів\n💰 Ціна за 1: {price_per} грн\n💵 Загальна сума: {total} грн\n\nДля нового замовлення оберіть бренд:",
                    reply_markup=create_main_keyboard()
                )
                if user_id in user_selection:
                    del user_selection[user_id]
        
        else:
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\n\nОберіть бренд:",
                reply_markup=create_main_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Помилка в handle_messages: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        message_id = call.message.message_id
        
        if call.data == "brand_dnipro":
            bot.edit_message_text(
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_models_keyboard()
            )
        
        elif call.data == "show_price":
            price_text = "📋 ПРАЙС Дніпро-М (ціна за 1 елемент):\n\n"
            for model_name, model_data in models_structure.items():
                price_text += f"🔋 {model_name} ({model_data['type']}):\n"
                for battery_name, battery_price in model_data["batteries"]:
                    price_text += f"  • {battery_name} — {battery_price} грн\n"
                price_text += "\n"
            bot.edit_message_text(
                price_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_main_keyboard()
            )
        
        elif call.data == "back_to_main":
            bot.edit_message_text(
                "Ремонт акумуляторів\n\nОберіть бренд:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_main_keyboard()
            )
        
        elif call.data == "back_to_models":
            bot.edit_message_text(
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_models_keyboard()
            )
        
        elif call.data == "back_to_batteries":
            if user_id in user_selection and 'model' in user_selection[user_id]:
                model_key = user_selection[user_id]['model']
                bot.edit_message_text(
                    f"Ремонт акумуляторів\nМодель: {model_key}\n\nОберіть тип акумулятора:",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=create_channel_battery_keyboard(model_key)
                )
        
        elif call.data.startswith("model_"):
            model_key = call.data.split("_")[1]
            if user_id not in user_selection:
                user_selection[user_id] = {}
            user_selection[user_id]['model'] = model_key
            bot.edit_message_text(
                f"Ремонт акумуляторів\nМодель: {model_key}\nТип: {models_structure[model_key]['type']}\n\nОберіть тип акумулятора:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_battery_keyboard(model_key)
            )
        
        elif call.data.startswith("battery_"):
            parts = call.data.split("_")
            model_key = parts[1]
            battery_name = " ".join(parts[2:]).replace("_", " ").replace("JP40,", "JP40")
            if user_id not in user_selection:
                user_selection[user_id] = {}
            user_selection[user_id]['model'] = model_key
            price = find_battery_price(model_key, battery_name)
            if price:
                user_selection[user_id]['battery_type'] = battery_name
                user_selection[user_id]['price_per_unit'] = price
                bot.edit_message_text(
                    f"Ремонт акумуляторів\nМодель: {model_key}\nТип АКБ: {battery_name}\nЦіна за 1: {price} грн\n\nОберіть кількість елементів:",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=create_channel_count_keyboard()
                )
        
        elif call.data.startswith("count_"):
            count = int(call.data.split("_")[1])
            if user_id in user_selection and 'battery_type' in user_selection[user_id]:
                model_key = user_selection[user_id]['model']
                battery_type = user_selection[user_id]['battery_type']
                price_per = user_selection[user_id]['price_per_unit']
                total = price_per * count
                bot.edit_message_text(
                    f"🧾 ЗАМОВЛЕННЯ:\n\n🔋 Модель: {model_key}\n⚡ Тип АКБ: {battery_type}\n📦 Кількість: {count} елементів\n💰 Ціна за 1: {price_per} грн\n💵 Загальна сума: {total} грн",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=create_channel_main_keyboard()
                )
                if user_id in user_selection:
                    del user_selection[user_id]
        
        bot.answer_callback_query(call.id)
    
    except Exception as e:
        logger.error(f"Помилка в handle_callback: {e}")

# ---------- ЗАПУСК БОТА ----------
def run_bot():
    """Запускає Telegram бота"""
    global TOKEN
    
    logger.info("🚀 Запуск Telegram бота...")
    
    # Очікуємо токен, якщо його немає
    while not TOKEN or TOKEN == "dummy_token":
        logger.info("⏸️ Очікуємо встановлення токена...")
        time.sleep(5)
        init_bot()  # Перевіряємо знову
    
    logger.info("✅ Токен отримано! Запускаємо бота...")
    
    # Спроба публікації в канал
    post_to_channel_with_retry()
    
    # Запуск полінга з перезапуском при помилках
    while True:
        try:
            logger.info("🔄 Бот очікує повідомлення...")
            bot.polling(none_stop=True, timeout=30, long_polling_timeout=30)
        except Exception as e:
            logger.error(f"Помилка полінга: {e}")
            logger.info("♻️ Перезапуск бота через 10 секунд...")
            time.sleep(10)

# ---------- ГОЛОВНА ФУНКЦІЯ ----------
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 БОТ ДЛЯ РЕМОНТУ АКУМУЛЯТОРІВ")
    print("⚙️  Версія для Render.com")
    print("=" * 50)
    
    # Ініціалізація бота
    init_bot()
    
    print(f"Токен встановлено: {'✅' if TOKEN and TOKEN != 'dummy_token' else '❌'}")
    print(f"Канал: {CHANNEL_ID}")
    
    # Запускаємо Flask в окремому потоці
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask сервер запущено")
    
    # Запускаємо Telegram бота
    run_bot()
