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

# ---------- ДАНІ ДЛЯ КАЛЬКУЛЯТОРА ----------
calculator_data = {
    "18650": {
        "element_capacity": "3000mAh",
        "prices": {
            # Для кожного типу елемента та кожної кількості - загальна ціна
            "2шт": {
                "Ampace JP30 36А": 5900,  # загальна ціна за 2 елементи + ремонт
                "EVE 30P 20A": 4300,
                "DMEGC 30P 20A": 4300
            },
            "3шт": {
                "Ampace JP30 36А": 8800,  # загальна ціна за 3 елементи + ремонт
                "EVE 30P 20A": 6400,
                "DMEGC 30P 20A": 6400
            },
            "4шт": {
                "Ampace JP30 36А": 11700,
                "EVE 30P 20A": 8500,
                "DMEGC 30P 20A": 8500
            },
            "5шт": {
                "Ampace JP30 36А": 14600,
                "EVE 30P 20A": 10600,
                "DMEGC 30P 20A": 10600
            },
            "6шт": {
                "Ampace JP30 36А": 17500,
                "EVE 30P 20A": 12700,
                "DMEGC 30P 20A": 12700
            },
            "10шт": {
                "Ampace JP30 36А": 29100,
                "EVE 30P 20A": 21100,
                "DMEGC 30P 20A": 21100
            },
            "12шт": {
                "Ampace JP30 36А": 34900,
                "EVE 30P 20A": 25300,
                "DMEGC 30P 20A": 25300
            },
            "15шт": {
                "Ampace JP30 36А": 43600,
                "EVE 30P 20A": 31600,
                "DMEGC 30P 20A": 31600
            },
            "20шт": {
                "Ampace JP30 36А": 58100,
                "EVE 30P 20A": 42100,
                "DMEGC 30P 20A": 42100
            }
        },
        "total_capacity": {
            "2шт": "6000mAh",
            "3шт": "9000mAh",
            "4шт": "6000mAh",
            "5шт": "3000mAh",
            "6шт": "9000mAh",
            "10шт": "15000mAh",
            "12шт": "12000mAh",
            "15шт": "15000mAh",
            "20шт": "12000mAh"
        }
    },
    "21700": {
        "element_capacity": "4000mAh",
        "prices": {
            "2шт": {
                "Ampace JP40 70А": 2800  # загальна ціна за 2 елементи + ремонт
            },
            "3шт": {
                "Ampace JP40 70А": 4150
            },
            "4шт": {
                "Ampace JP40 70А": 5500
            },
            "5шт": {
                "Ampace JP40 70А": 6850
            },
            "6шт": {
                "Ampace JP40 70А": 8200
            },
            "10шт": {
                "Ampace JP40 70А": 13600
            },
            "12шт": {
                "Ampace JP40 70А": 16300
            },
            "15шт": {
                "Ampace JP40 70А": 20350
            },
            "20шт": {
                "Ampace JP40 70А": 27100
            }
        },
        "total_capacity": {
            "2шт": "8000mAh",
            "3шт": "12000mAh",
            "4шт": "8000mAh",
            "5шт": "4000mAh",
            "6шт": "12000mAh",
            "10шт": "20000mAh",
            "12шт": "16000mAh",
            "15шт": "20000mAh",
            "20шт": "16000mAh"
        }
    }
}

# ДАНІ З ВИХІДНОЮ ЄМНІСТЮ (для Дніпро-M)
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
user_calculator = {}

# ---------- КЛАВІАТУРИ ----------
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Дніпро-M", "Калькулятор", "Гарантія", "Відправка та оплата")
    return keyboard

def create_models_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = list(models_structure.keys())
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.add("◀️ Назад")
    return keyboard

def create_battery_type_keyboard(model_key):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    batteries = models_structure[model_key]["batteries"]
    for battery_name, battery_capacity, battery_price in batteries:
        keyboard.add(f"{battery_name} - {battery_price} грн")
    keyboard.add("◀️ Назад до моделей")
    return keyboard

def create_count_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    numbers = [str(i) for i in range(1, 11)]
    keyboard.add(*numbers[:5])
    keyboard.add(*numbers[5:])
    keyboard.add("◀️ Назад до типів АКБ")
    return keyboard

def create_calculator_format_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("18650", "21700")
    keyboard.add("◀️ Назад")
    return keyboard

def create_calculator_count_keyboard(format_type):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    counts = list(calculator_data[format_type]["prices"].keys())
    
    # Розділяємо на рядки по 3 кнопки
    for i in range(0, len(counts), 3):
        row = counts[i:i+3]
        keyboard.add(*row)
    
    keyboard.add("◀️ Назад до вибору формату")
    return keyboard

def create_calculator_battery_keyboard(format_type, count):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    prices_for_count = calculator_data[format_type]["prices"][count]
    
    for battery_name, total_price in prices_for_count.items():
        button_text = f"{battery_name} - {total_price} грн"
        keyboard.add(button_text)
    
    keyboard.add("◀️ Назад до кількості")
    return keyboard

def create_channel_main_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Дніпро-M", callback_data="brand_dnipro"),
        types.InlineKeyboardButton("Калькулятор", callback_data="show_calculator"),
        types.InlineKeyboardButton("Гарантія", callback_data="warranty"),
        types.InlineKeyboardButton("Відправка та оплата", callback_data="shipping_payment")
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
    
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_channel_battery_keyboard(model_key):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    batteries = models_structure[model_key]["batteries"]
    for battery_name, battery_capacity, battery_price in batteries:
        clean_name = battery_name.replace(" ", "_").replace(",", "")
        callback_data = f"battery_{model_key}_{clean_name}"
        button_text = f"{battery_name} - {battery_price} грн"
        keyboard.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_models"))
    return keyboard

def create_channel_calculator_format_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("18650", callback_data="calc_18650"),
        types.InlineKeyboardButton("21700", callback_data="calc_21700")
    )
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_channel_calculator_count_keyboard(format_type):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    counts = list(calculator_data[format_type]["prices"].keys())
    
    buttons = []
    for count in counts:
        buttons.append(types.InlineKeyboardButton(count, callback_data=f"calc_{format_type}_{count}"))
    
    for i in range(0, len(buttons), 3):
        if i + 2 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1], buttons[i+2])
        elif i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="calc_back_format"))
    return keyboard

# ---------- ОБРОБНИКИ ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Ремонт акумуляторів\n\nОберіть опцію:",
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Головне меню
    if text == "Дніпро-M":
        user_selection[user_id] = {'brand': 'Дніпро-M'}
        bot.send_message(
            chat_id,
            "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
            reply_markup=create_models_keyboard()
        )
    
    elif text == "Калькулятор":
        user_calculator[user_id] = {'step': 'format'}
        bot.send_message(
            chat_id,
            "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
            "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
            "**Оберіть формат елементів:**",
            reply_markup=create_calculator_format_keyboard(),
            parse_mode="Markdown"
        )
    
    elif text == "Гарантія":
        warranty_text = (
            "📜 ГАРАНТІЯ:\n\n"
            "✅ На всі відремонтовані акумулятори надається гарантія:\n"
            "• 3 місяці на елементи акумулятора\n"
            "• 6 місяців на пайку та збірку\n"
            "• Гарантія діє з моменту отримання\n"
            "• У разі виникнення проблем - безкоштовний ремонт або заміна\n\n"
            "📞 Контакти для гарантійних питань:\n"
            "• Телефон: +380 XX XXX XX XX\n"
            "• Email: example@email.com"
        )
        bot.send_message(chat_id, warranty_text, reply_markup=create_main_keyboard())
    
    elif text == "Відправка та оплата":
        shipping_text = (
            "🚚 ВІДПРАВКА ТА ОПЛАТА:\n\n"
            "📦 Варіанти відправки:\n"
            "• Нова Пошта - 1-3 дні\n"
            "• Доставка по м.Надвірна(Безкоштовна)\n\n"
            "💳 Оплата на карту перед відправкою:\n"
            "• Стандартний ремонт - 1-3 дні\n"
        )
        bot.send_message(chat_id, shipping_text, reply_markup=create_main_keyboard())
    
    # Обробка кнопки "Назад"
    elif text == "◀️ Назад":
        bot.send_message(
            chat_id,
            "Ремонт акумуляторів\n\nОберіть опцію:",
            reply_markup=create_main_keyboard()
        )
    
    elif text == "◀️ Назад до моделей":
        bot.send_message(
            chat_id,
            "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
            reply_markup=create_models_keyboard()
        )
    
    elif text == "◀️ Назад до типів АКБ":
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
    
    elif text == "◀️ Назад до вибору формату":
        user_calculator[user_id] = {'step': 'format'}
        bot.send_message(
            chat_id,
            "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
            "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
            "**Оберіть формат елементів:**",
            reply_markup=create_calculator_format_keyboard(),
            parse_mode="Markdown"
        )
    
    elif text == "◀️ Назад до кількості":
        if user_id in user_calculator and 'format' in user_calculator[user_id]:
            format_type = user_calculator[user_id]['format']
            bot.send_message(
                chat_id,
                f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                f"**Формат:** {format_type}\n"
                f"**Ємність одного елемента:** {calculator_data[format_type]['element_capacity']}\n\n"
                f"**Оберіть кількість елементів:**",
                reply_markup=create_calculator_count_keyboard(format_type),
                parse_mode="Markdown"
            )
    
    # Обробка вибору формату для калькулятора
    elif text in ["18650", "21700"]:
        if user_id not in user_calculator:
            user_calculator[user_id] = {}
        user_calculator[user_id]['format'] = text
        user_calculator[user_id]['step'] = 'count'
        
        bot.send_message(
            chat_id,
            f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
            f"**Формат:** {text}\n"
            f"**Ємність одного елемента:** {calculator_data[text]['element_capacity']}\n\n"
            f"**Оберіть кількість елементів:**",
            reply_markup=create_calculator_count_keyboard(text),
            parse_mode="Markdown"
        )
    
    # Обробка вибору кількості елементів для калькулятора
    elif text.endswith("шт") and text[:-2].isdigit():
        if user_id in user_calculator and 'format' in user_calculator[user_id]:
            format_type = user_calculator[user_id]['format']
            count = text
            
            # Перевіряємо чи така кількість є в даних
            if count in calculator_data[format_type]["prices"]:
                user_calculator[user_id]['count'] = count
                user_calculator[user_id]['step'] = 'battery'
                
                total_capacity = calculator_data[format_type]["total_capacity"][count]
                prices_for_count = calculator_data[format_type]["prices"][count]
                
                # Формуємо повідомлення з вибором елементів
                if format_type == "18650":
                    elements_text = "**Для 18650:**\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                else:  # 21700
                    elements_text = "**Для 21700:**\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                
                bot.send_message(
                    chat_id,
                    f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                    f"**Формат:** {format_type}\n"
                    f"**Кількість елементів:** {count}\n"
                    f"**Вихідна ємність після перепаковки:** {total_capacity}\n\n"
                    f"{elements_text}\n"
                    f"**Оберіть тип елемента:**",
                    reply_markup=create_calculator_battery_keyboard(format_type, count),
                    parse_mode="Markdown"
                )
    
    # Обробка вибору типу елемента для калькулятора
    elif " - " in text and " грн" in text and user_id in user_calculator and user_calculator[user_id].get('step') == 'battery':
        parts = text.split(" - ")
        battery_name = parts[0].strip()
        total_price_str = parts[1].replace(" грн", "").strip()
        total_price = int(total_price_str)
        
        if user_id in user_calculator and 'format' in user_calculator[user_id] and 'count' in user_calculator[user_id]:
            format_type = user_calculator[user_id]['format']
            count = user_calculator[user_id]['count']
            count_num = int(count[:-2])  # Прибираємо "шт"
            
            total_capacity = calculator_data[format_type]["total_capacity"][count]
            element_capacity = calculator_data[format_type]["element_capacity"]
            
            # Формуємо фінальне повідомлення
            final_text = (
                f"🧮 **РЕЗУЛЬТАТ РОЗРАХУНКУ**\n\n"
                f"**Формат елементів:** {format_type}\n"
                f"**Кількість елементів:** {count}\n"
                f"**Тип елемента:** {battery_name}\n"
                f"**Ємність одного елемента:** {element_capacity}\n"
                f"**Вихідна ємність після перепаковки:** {total_capacity}\n\n"
                f"**ЗАГАЛЬНА ВАРТІСТЬ: {total_price} грн**\n\n"
                f"*Ціна вже включає вартість елементів та роботу з ремонту*\n\n"
                f"Для нового розрахунку оберіть 'Калькулятор' в головному меню."
            )
            
            bot.send_message(
                chat_id,
                final_text,
                reply_markup=create_main_keyboard(),
                parse_mode="Markdown"
            )
            
            # Очищаємо дані калькулятора
            if user_id in user_calculator:
                del user_calculator[user_id]
    
    # Обробка вибору моделі (Дніпро-M)
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
    
    # Обробка вибору типу акумулятора (Дніпро-M)
    elif " - " in text and " грн" in text and user_id in user_selection and 'model' in user_selection[user_id]:
        parts = text.split(" - ")
        battery_name = parts[0].strip()
        battery_price = parts[1].replace(" грн", "").strip()
        
        if user_id in user_selection and 'model' in user_selection[user_id]:
            model_key = user_selection[user_id]['model']
            
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
    
    # Обробка вибору кількості (Дніпро-M)
    elif text.isdigit() and 1 <= int(text) <= 10 and user_id in user_selection and 'battery_type' in user_selection[user_id]:
        count = int(text)
        model = user_selection[user_id]['model']
        battery_type = user_selection[user_id]['battery_type']
        battery_capacity = user_selection[user_id]['battery_capacity']
        price_per = user_selection[user_id]['price']
        total = price_per * count
        
        bot.send_message(
            chat_id,
            f"🧾 **РОЗРАХУНОК ВАРТОСТІ**\n\n"
            f"🔋 Модель: {model}\n"
            f"⚡ Тип акумулятора: {battery_type}\n"
            f"📊 Вихідна ємність: {battery_capacity}\n"
            f"📦 Кількість: {count} шт.\n"
            f"💰 Ціна за 1: {price_per} грн\n"
            f"💵 Загальна вартість: {total} грн\n\n"
            f"Для нового розрахунку оберіть опцію:",
            reply_markup=create_main_keyboard()
        )
        del user_selection[user_id]
    
    else:
        bot.send_message(
            chat_id,
            "Ремонт акумуляторів\n\nОберіть опцію:",
            reply_markup=create_main_keyboard()
        )

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
    
    elif call.data == "show_calculator":
        bot.edit_message_text(
            "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
            "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
            "**Оберіть формат елементів:**",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_calculator_format_keyboard(),
            parse_mode="Markdown"
        )
    
    elif call.data == "warranty":
        warranty_text = (
            "📜 ГАРАНТІЯ:\n\n"
            "❌ Гарантія на бмс ненадається навіть у випадку заміни(Дніпро-М)\n"
            "✅ На всі відремонтовані акумулятори надається гарантія:\n"
            "• 6 місяці на елементи акумулятора\n"
            "• 6 місяців на зварку та збірку\n"
            "• Гарантія діє з моменту отримання\n"
            "• У разі виникнення проблем - безкоштовний ремонт"
        )
        bot.edit_message_text(
            warranty_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_main_keyboard()
        )
    
    elif call.data == "shipping_payment":
        shipping_text = (
            "🚚 ВІДПРАВКА ТА ОПЛАТА:\n\n"
            "📦 Варіанти відправки:\n"
            "• Нова Пошта - 1-3 дні\n"
            "• Доставка по м.Надвірна(Безкоштовна)\n\n"
            "💳 Оплата на карту перед відправкою:\n"
            "• Стандартний ремонт - 1-3 дні\n"
            "• Алреса відправки м.Надвірна відділення нової пошти №1 тел:0980626364 Ящук Роман\n"
            "• перед відправкою телефонуєте або пишете в Телеграм або Вайбер\n"
        )
        bot.edit_message_text(
            shipping_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_main_keyboard()
        )
    
    elif call.data == "back_to_main":
        bot.edit_message_text(
            "Ремонт акумуляторів\n\nОберіть опцію:",
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
    
    elif call.data == "calc_back_format":
        bot.edit_message_text(
            "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
            "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
            "**Оберіть формат елементів:**",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_channel_calculator_format_keyboard(),
            parse_mode="Markdown"
        )
    
    elif call.data.startswith("calc_"):
        parts = call.data.split("_")
        
        if len(parts) == 2:  # calc_18650 або calc_21700
            format_type = parts[1]
            bot.edit_message_text(
                f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                f"**Формат:** {format_type}\n"
                f"**Ємність одного елемента:** {calculator_data[format_type]['element_capacity']}\n\n"
                f"**Оберіть кількість елементів:**",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=create_channel_calculator_count_keyboard(format_type),
                parse_mode="Markdown"
            )
        
        elif len(parts) == 3:  # calc_18650_2шт
            format_type = parts[1]
            count = parts[2]
            
            if count in calculator_data[format_type]["prices"]:
                total_capacity = calculator_data[format_type]["total_capacity"][count]
                prices_for_count = calculator_data[format_type]["prices"][count]
                
                # Формуємо повідомлення з інформацією
                if format_type == "18650":
                    elements_text = "**Для 18650:**\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                else:  # 21700
                    elements_text = "**Для 21700:**\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                
                info_text = (
                    f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                    f"**Формат:** {format_type}\n"
                    f"**Кількість елементів:** {count}\n"
                    f"**Вихідна ємність після перепаковки:** {total_capacity}\n\n"
                    f"{elements_text}\n"
                    f"Для вибору елементів та детального розрахунку напишіть боту /start та оберіть 'Калькулятор'"
                )
                
                bot.edit_message_text(
                    info_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=create_channel_main_keyboard(),
                    parse_mode="Markdown"
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
            "Ремонт акумуляторів\n\nОберіть опцію:",
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
