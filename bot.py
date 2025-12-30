import telebot
from telebot import types
import time
import logging
import os
from flask import Flask
import threading
import requests

# ==================== КОНФІГУРАЦІЯ ====================
TOKEN = "8252548275:AAF0qYbEZCoBPEN6gNHx2kkYi9gHoUPNKrA"
CHANNEL_ID = "@tester_avto"

# АВТОМАТИЧНЕ СКИДАННЯ ВЕБХУКА
def reset_webhook():
    """Автоматично скидає вебхук при запуску"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
        response = requests.get(url, timeout=5)
        if response.json().get('ok'):
            print("✅ Вебхук успішно скинуто!")
            return True
        else:
            print("⚠️ Не вдалося скинути вебхук автоматично")
            return False
    except Exception as e:
        print(f"⚠️ Помилка скидання вебхука: {e}")
        return False

# Скидаємо вебхук перед створенням бота
reset_webhook()

# Створюємо бота
bot = telebot.TeleBot(TOKEN)
print("=" * 50)
print("🤖 БОТ ДЛЯ РЕМОНТУ АКУМУЛЯТОРІВ")
print(f"✅ Токен: {TOKEN[:10]}...")
print(f"✅ Канал: {CHANNEL_ID}")
print("=" * 50)
# =====================================================

# Flask для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот працює! Telegram: @tester_avto"

@app.route('/reset')
def web_reset():
    """Сторінка для ручного скидання вебхука"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        return f"✅ Вебхук скинуто: {response.text}"
    except:
        return "❌ Помилка скидання вебхука"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------- ДАНІ З ВИХІДНОЮ ЄМНІСТЮ ----------
# Формат: (назва, ємність (mAh), ціна)
models_structure = {
    "BP‑122 12V / 2.0Ah": {
        "type": "12V блок",
        "capacity": "3000mAh",
        "voltage": "12V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 850),
            ("EVE 30P 3000mAh 20A", "3000mAh", 700),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 700),
        ]
    },
    "BP‑125 12V / 4.0Ah": {
        "type": "12V блок", 
        "capacity": "6000mAh",
        "voltage": "12V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 1500),
            ("EVE 30P 3000mAh 20A", "3000mAh", 1200),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 1200),
        ]
    },
    "BP‑220 (2 Ah)": {
        "type": "18650",
        "capacity": "3000mAh",
        "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 1250),
            ("EVE 30P 3000mAh 20A", "3000mAh", 900),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 900),
        ]
    },
    "BP‑240 (4 Ah)": {
        "type": "18650", 
        "capacity": "6000mAh",
        "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 2000),
            ("EVE 30P 3000mAh 20A", "3000mAh", 1600),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 1600),
        ]
    },
    "BP‑260 (6 Ah)": {
        "type": "18650",
        "capacity": "9000mAh",
        "voltage": "20V",
        "batteries": [
            ("Ampace JP30 3000mAh 36А", "3000mAh", 2900),
            ("EVE 30P 3000mAh 20A", "3000mAh", 2100),
            ("DMEGC 30P 3000mAh 20A", "3000mAh", 2100),
        ]
    },
    "BP‑240N (4 Ah)": {
        "type": "21700",
        "capacity": "4000mAh",
        "voltage": "20V",
        "batteries": [
            ("Ampace JP40 70А", "4000mAh", 1350),
        ]
    },
    "BP‑280N (8 Ah)": {
        "type": "21700",
        "capacity": "8000mAh",
        "voltage": "20V",
        "batteries": [
            ("Ampace JP40 70А", "4000mAh", 2200),
        ]
    }
}

user_selection = {}

# ---------- КЛАВІАТУРИ ----------
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Дніпро-M", "Прайс")
    return keyboard

def create_models_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = list(models_structure.keys())
    
    # Додаємо кнопки по 2 в ряд
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
    for battery_name, battery_capacity, battery_price in batteries:
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
    
    # Додаємо кнопки по 2 в ряд
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
    for battery_name, battery_capacity, battery_price in batteries:
        clean_name = battery_name.replace(" ", "_").replace(",", "")
        callback_data = f"battery_{model_key}_{clean_name}"
        button_text = f"{battery_name} - {battery_price} грн"
        keyboard.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="back_to_models"))
    return keyboard

# ---------- ОБРОБНИКИ ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Ремонт акумуляторів\n\nОберіть бренд:",
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
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
        price_text = "📋 ПРАЙС Дніпро-М (ціна за 1 акумулятор):\n\n"
        for model_name, model_data in models_structure.items():
            price_text += f"\n🔋 {model_name}:\n"
            price_text += f"  Напруга: {model_data.get('voltage', 'Н/Д')}\n"
            price_text += f"  Вихідна ємність: {model_data['capacity']}\n"
            price_text += f"  Тип: {model_data['type']}\n"
            for battery_name, battery_capacity, battery_price in model_data["batteries"]:
                price_text += f"  • {battery_name} — {battery_price} грн\n"
        
        bot.send_message(chat_id, price_text, reply_markup=create_main_keyboard())
    
    elif text == "Назад":
        bot.send_message(
            chat_id,
            "Ремонт акумуляторів\n\nОберіть бренд:",
            reply_markup=create_main_keyboard()
        )
    
    elif text in models_structure:
        user_selection[user_id] = {'model': text}
        model_data = models_structure[text]
        bot.send_message(
            chat_id,
            f"Ремонт акумуляторів\n"
            f"🔋 Модель: {text}\n"
            f"⚡ Напруга: {model_data.get('voltage', 'Н/Д')}\n"
            f"📊 Вихідна ємність: {model_data['capacity']}\n"
            f"🔧 Тип: {model_data['type']}\n\n"
            f"Оберіть тип акумулятора:",
            reply_markup=create_battery_type_keyboard(text)
        )
    
    elif " - " in text and " грн" in text:
        parts = text.split(" - ")
        battery_name = parts[0].strip()
        battery_price = parts[1].replace(" грн", "").strip()
        
        if user_id in user_selection and 'model' in user_selection[user_id]:
            model_key = user_selection[user_id]['model']
            
            # Знаходимо ємність акумулятора
            battery_capacity = ""
            for name, capacity, price in models_structure[model_key]["batteries"]:
                if name == battery_name:
                    battery_capacity = capacity
                    break
            
            user_selection[user_id]['battery_type'] = battery_name
            user_selection[user_id]['battery_capacity'] = battery_capacity
            user_selection[user_id]['price'] = int(battery_price)
            
            bot.send_message(
                chat_id,
                f"✅ Ви обрали:\n\n"
                f"🔋 Модель: {user_selection[user_id]['model']}\n"
                f"⚡ Тип акумулятора: {battery_name}\n"
                f"📊 Вихідна ємність: {battery_capacity}\n"
                f"💰 Ціна: {battery_price} грн\n\n"
                f"Тепер оберіть кількість акумуляторів:",
                reply_markup=create_count_keyboard()
            )
    
    elif text.isdigit() and 1 <= int(text) <= 10:
        if user_id in user_selection and 'battery_type' in user_selection[user_id]:
            count = int(text)
            model = user_selection[user_id]['model']
            battery_type = user_selection[user_id]['battery_type']
            battery_capacity = user_selection[user_id]['battery_capacity']
            price_per = user_selection[user_id]['price']
            total = price_per * count
            
            bot.send_message(
                chat_id,
                f"🧾 РОЗРАХУНОК ВАРТОСТІ:\n\n"
                f"🔋 Модель: {model}\n"
                f"⚡ Тип акумулятора: {battery_type}\n"
                f"📊 Вихідна ємність: {battery_capacity}\n"
                f"📦 Кількість: {count} шт.\n"
                f"💰 Ціна за 1: {price_per} грн\n"
                f"💵 Загальна вартість: {total} грн\n\n"
                f"Для нового розрахунку оберіть бренд:",
                reply_markup=create_main_keyboard()
            )
            del user_selection[user_id]

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "brand_dnipro":
        bot.edit_message_text(
            "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_models_keyboard()
        )
    
    elif call.data == "show_price":
        price_text = "📋 ПРАЙС Дніпро-М (ціна за 1 акумулятор):\n\n"
        for model_name, model_data in models_structure.items():
            price_text += f"🔋 {model_name}:\n"
            price_text += f"  Напруга: {model_data.get('voltage', 'Н/Д')}\n"
            price_text += f"  Вихідна ємність: {model_data['capacity']}\n"
            price_text += f"  Тип: {model_data['type']}\n"
            for battery_name, battery_capacity, battery_price in model_data["batteries"]:
                price_text += f"  • {battery_name} — {battery_price} грн\n"
            price_text += "\n"
        bot.edit_message_text(
            price_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_main_keyboard()
        )
    
    elif call.data.startswith("model_"):
        model_key = call.data.split("_")[1]
        model_data = models_structure[model_key]
        bot.edit_message_text(
            f"Ремонт акумуляторів\n"
            f"🔋 Модель: {model_key}\n"
            f"⚡ Напруга: {model_data.get('voltage', 'Н/Д')}\n"
            f"📊 Вихідна ємність: {model_data['capacity']}\n"
            f"🔧 Тип: {model_data['type']}\n\n"
            f"Оберіть тип акумулятора:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_battery_keyboard(model_key)
        )
    
    elif call.data.startswith("battery_"):
        parts = call.data.split("_")
        model_key = parts[1]
        battery_name = " ".join(parts[2:]).replace("_", " ").replace("JP40,", "JP40")
        
        # Знаходимо дані акумулятора
        battery_capacity = ""
        battery_price = 0
        for name, capacity, price in models_structure[model_key]["batteries"]:
            if name == battery_name:
                battery_capacity = capacity
                battery_price = price
                break
        
        if battery_price:
            bot.edit_message_text(
                f"✅ Ви обрали:\n\n"
                f"🔋 Модель: {model_key}\n"
                f"⚡ Тип акумулятора: {battery_name}\n"
                f"📊 Вихідна ємність: {battery_capacity}\n"
                f"💰 Ціна: {battery_price} грн\n\n"
                f"Для розрахунку вартості напишіть боту /start",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_main_keyboard()
            )
    
    bot.answer_callback_query(call.id)

# ---------- ПУБЛІКАЦІЯ В КАНАЛ ----------
def post_to_channel():
    try:
        bot.send_message(
            CHANNEL_ID,
            "Ремонт акумуляторів\n\nОберіть бренд:",
            reply_markup=create_channel_main_keyboard()
        )
        return True
    except Exception as e:
        logger.error(f"Помилка: {e}")
        return False

# ---------- ЗАПУСК БОТА ----------
def run_telegram_bot():
    logger.info("🚀 Запуск бота...")
    
    if post_to_channel():
        logger.info("✅ Бот запущений")
    else:
        logger.warning("⚠️ Проблема з публікацією")
    
    logger.info("🔄 Бот очікує повідомлення...")
    
    try:
        bot.polling(none_stop=True, timeout=30)
    except Exception as e:
        if "409" in str(e) or "Conflict" in str(e):
            logger.error("🔌 Конфлікт! Скидаю вебхук...")
            reset_webhook()
            time.sleep(5)
            run_telegram_bot()
        else:
            logger.error(f"💥 Помилка: {e}")
            time.sleep(10)
            run_telegram_bot()

# ---------- ГОЛОВНИЙ КОД ----------
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask сервер запущено")
    
    run_telegram_bot()
