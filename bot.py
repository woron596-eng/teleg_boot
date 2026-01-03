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
        bot.send_message(
            config.CHANNEL_ID,
            "🚀 *Бот для ремонту акумуляторів запущений!*\n\n"
            "📱 *Оберіть опцію:*",
            parse_mode="Markdown",
            reply_markup=menu.create_channel_main_keyboard()
        )
        logger.info("✅ Пост успішно опубліковано в канал")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка публікації в канал: {e}")
        
        # Спробуємо через API
        try:
            url = f"https://api.telegram.org/bot{config.TOKEN}/sendMessage"
            data = {
                "chat_id": config.CHANNEL_ID,
                "text": "🚀 Бот для ремонту акумуляторів запущений!\n\n📱 Оберіть опцію:",
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "Дніпро-M", "callback_data": "brand_dnipro"},
                        {"text": "Калькулятор", "callback_data": "show_calculator"}
                    ], [
                        {"text": "Гарантія", "callback_data": "warranty"},
                        {"text": "Відправка та оплата", "callback_data": "shipping_payment"}
                    ]]
                }
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Пост опубліковано через API")
                return True
        except Exception as api_error:
            logger.error(f"❌ Помилка API: {api_error}")
        
        return False

# ---------- ОБРОБНИКИ КОМАНД ----------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    try:
        bot.send_message(
            message.chat.id,
            "🔋 *Ремонт акумуляторів*\n\nОберіть опцію:",
            reply_markup=menu.create_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")

# ---------- ОБРОБНИКИ ДЛЯ КНОПОК ГОЛОВНОГО МЕНЮ ----------
@bot.message_handler(func=lambda message: message.text == "Дніпро-M")
def handle_dnipro(message):
    try:
        menu.user_selection[message.from_user.id] = {'brand': 'Дніпро-M'}
        bot.send_message(
            message.chat.id,
            "🔋 *Ремонт акумуляторів*\nБренд: *Дніпро-M*\n\nОберіть модель АКБ:",
            reply_markup=menu.create_models_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_dnipro: {e}")

@bot.message_handler(func=lambda message: message.text == "Калькулятор")
def handle_calculator(message):
    try:
        menu.user_calculator[message.from_user.id] = {'step': 'format'}
        bot.send_message(
            message.chat.id,
            "🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
            "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
            "*Оберіть формат елементів:*",
            reply_markup=menu.create_calculator_format_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_calculator: {e}")

@bot.message_handler(func=lambda message: message.text == "Гарантія")
def handle_warranty(message):
    try:
        warranty_text = (
            "📜 *ГАРАНТІЯ:*\n\n"
            "✅ На всі відремонтовані акумулятори надається гарантія:\n"
            "• 3 місяці на елементи акумулятора\n"
            "• 6 місяців на пайку та збірку\n"
            "• Гарантія діє з моменту отримання\n"
            "• У разі виникнення проблем - безкоштовний ремонт або заміна"
        )
        bot.send_message(
            message.chat.id, 
            warranty_text,
            reply_markup=menu.create_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_warranty: {e}")

@bot.message_handler(func=lambda message: message.text == "Відправка та оплата")
def handle_shipping(message):
    try:
        shipping_text = (
            "🚚 *ВІДПРАВКА ТА ОПЛАТА:*\n\n"
            "📦 *Варіанти відправки:*\n"
            "• Нова Пошта - 1-3 дні\n"
            "• Доставка по м.Надвірна (Безкоштовна)\n\n"
            "💳 *Оплата на карту перед відправкою:*\n"
            "• Стандартний ремонт - 1-3 дні"
        )
        bot.send_message(
            message.chat.id, 
            shipping_text,
            reply_markup=menu.create_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_shipping: {e}")

# ---------- ОБРОБНИКИ КНОПОК "НАЗАД" ----------
@bot.message_handler(func=lambda message: message.text == "◀️ Назад")
def handle_back(message):
    try:
        bot.send_message(
            message.chat.id,
            "🔋 *Ремонт акумуляторів*\n\nОберіть опцію:",
            reply_markup=menu.create_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_back: {e}")

@bot.message_handler(func=lambda message: message.text == "◀️ Назад до моделей")
def handle_back_to_models(message):
    try:
        bot.send_message(
            message.chat.id,
            "🔋 *Ремонт акумуляторів*\nБренд: *Дніпро-M*\n\nОберіть модель АКБ:",
            reply_markup=menu.create_models_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_back_to_models: {e}")

# ---------- ОБРОБНИК ВИБОРУ МОДЕЛІ ----------
@bot.message_handler(func=lambda message: message.text in config.MODELS_STRUCTURE)
def handle_model_selection(message):
    try:
        model_key = message.text
        menu.user_selection[message.from_user.id] = {'model': model_key}
        model_data = config.MODELS_STRUCTURE[model_key]
        
        bot.send_message(
            message.chat.id,
            f"🔋 *Ремонт акумуляторів*\n"
            f"Модель: *{model_key}*\n"
            f"Напруга: {model_data.get('voltage', 'Н/Д')}\n"
            f"Вихідна ємність: {model_data['capacity']}\n"
            f"Тип: {model_data['type']}\n\n"
            f"*Оберіть тип акумулятора:*",
            reply_markup=menu.create_battery_type_keyboard(model_key),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_model_selection: {e}")

# ---------- ОБРОБНИК ВИБОРУ ТИПУ АКБ ----------
@bot.message_handler(func=lambda message: " - " in message.text and " грн" in message.text)
def handle_battery_selection(message):
    try:
        parts = message.text.split(" - ")
        battery_name = parts[0].strip()
        battery_price = parts[1].replace(" грн", "").strip()
        
        user_id = message.from_user.id
        
        if user_id in menu.user_selection and 'model' in menu.user_selection[user_id]:
            model_key = menu.user_selection[user_id]['model']
            
            # Знаходимо ємність батареї
            battery_capacity = ""
            for name, capacity, price in config.MODELS_STRUCTURE[model_key]["batteries"]:
                if name == battery_name:
                    battery_capacity = capacity
                    break
            
            # Зберігаємо вибір
            menu.user_selection[user_id]['battery_type'] = battery_name
            menu.user_selection[user_id]['battery_capacity'] = battery_capacity
            menu.user_selection[user_id]['price'] = int(battery_price)
            
            bot.send_message(
                message.chat.id,
                f"✅ *Ви обрали:*\n\n"
                f"🔋 Модель: {model_key}\n"
                f"⚡ Тип акумулятора: {battery_name}\n"
                f"📊 Вихідна ємність: {battery_capacity}\n"
                f"💰 Ціна: {battery_price} грн\n\n"
                f"*Тепер оберіть кількість акумуляторів:*",
                reply_markup=menu.create_count_keyboard(),
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                "⚠️ Спочатку оберіть модель акумулятора",
                reply_markup=menu.create_main_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in handle_battery_selection: {e}")

# ---------- ОБРОБНИК ВИБОРУ КІЛЬКОСТІ ----------
@bot.message_handler(func=lambda message: message.text.isdigit() and 1 <= int(message.text) <= 10)
def handle_quantity_selection(message):
    try:
        user_id = message.from_user.id
        
        if user_id in menu.user_selection and 'battery_type' in menu.user_selection[user_id]:
            count = int(message.text)
            model = menu.user_selection[user_id]['model']
            battery_type = menu.user_selection[user_id]['battery_type']
            battery_capacity = menu.user_selection[user_id]['battery_capacity']
            price_per = menu.user_selection[user_id]['price']
            total = price_per * count
            
            bot.send_message(
                message.chat.id,
                f"🧾 *РОЗРАХУНОК ВАРТОСТІ*\n\n"
                f"🔋 Модель: {model}\n"
                f"⚡ Тип акумулятора: {battery_type}\n"
                f"📊 Вихідна ємність: {battery_capacity}\n"
                f"📦 Кількість: {count} шт.\n"
                f"💰 Ціна за 1: {price_per} грн\n"
                f"💵 *Загальна вартість: {total} грн*\n\n"
                f"Для нового розрахунку оберіть опцію:",
                reply_markup=menu.create_main_keyboard(),
                parse_mode="Markdown"
            )
            
            # Очищаємо вибір користувача
            if user_id in menu.user_selection:
                del menu.user_selection[user_id]
        else:
            bot.send_message(
                message.chat.id,
                "⚠️ Спочатку оберіть тип акумулятора",
                reply_markup=menu.create_main_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in handle_quantity_selection: {e}")

# ---------- ОБРОБНИКИ КАЛЬКУЛЯТОРА ----------
@bot.message_handler(func=lambda message: message.text in ["18650", "21700"])
def handle_calculator_format(message):
    try:
        user_id = message.from_user.id
        if user_id not in menu.user_calculator:
            menu.user_calculator[user_id] = {}
        
        menu.user_calculator[user_id]['format'] = message.text
        menu.user_calculator[user_id]['step'] = 'count'
        
        bot.send_message(
            message.chat.id,
            f"🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
            f"*Формат:* {message.text}\n"
            f"*Ємність одного елемента:* {config.CALCULATOR_DATA[message.text]['element_capacity']}\n\n"
            f"*Оберіть кількість елементів:*",
            reply_markup=menu.create_calculator_count_keyboard(message.text),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in handle_calculator_format: {e}")

@bot.message_handler(func=lambda message: message.text.endswith("шт") and message.text[:-2].isdigit())
def handle_calculator_count(message):
    try:
        user_id = message.from_user.id
        
        if user_id in menu.user_calculator and 'format' in menu.user_calculator[user_id]:
            format_type = menu.user_calculator[user_id]['format']
            count = message.text
            
            if count in config.CALCULATOR_DATA[format_type]["prices"]:
                menu.user_calculator[user_id]['count'] = count
                menu.user_calculator[user_id]['step'] = 'battery'
                
                total_capacity = config.CALCULATOR_DATA[format_type]["total_capacity"][count]
                prices_for_count = config.CALCULATOR_DATA[format_type]["prices"][count]
                
                if format_type == "18650":
                    elements_text = "*Для 18650:*\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                else:
                    elements_text = "*Для 21700:*\n"
                    for battery_name, total_price in prices_for_count.items():
                        elements_text += f"• {battery_name} - {total_price} грн\n"
                
                bot.send_message(
                    message.chat.id,
                    f"🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\n"
                    f"*Формат:* {format_type}\n"
                    f"*Кількість елементів:* {count}\n"
                    f"*Вихідна ємність після перепаковки:* {total_capacity}\n\n"
                    f"{elements_text}\n"
                    f"*Оберіть тип елемента:*",
                    reply_markup=menu.create_calculator_battery_keyboard(format_type, count),
                    parse_mode="Markdown"
                )
    except Exception as e:
        logger.error(f"Error in handle_calculator_count: {e}")

@bot.message_handler(func=lambda message: " - " in message.text and " грн" in message.text and 
                     message.from_user.id in menu.user_calculator and 
                     menu.user_calculator[message.from_user.id].get('step') == 'battery')
def handle_calculator_battery(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split(" - ")
        battery_name = parts[0].strip()
        total_price_str = parts[1].replace(" грн", "").strip()
        total_price = int(total_price_str)
        
        if user_id in menu.user_calculator and 'format' in menu.user_calculator[user_id] and 'count' in menu.user_calculator[user_id]:
            format_type = menu.user_calculator[user_id]['format']
            count = menu.user_calculator[user_id]['count']
            
            total_capacity = config.CALCULATOR_DATA[format_type]["total_capacity"][count]
            element_capacity = config.CALCULATOR_DATA[format_type]["element_capacity"]
            
            final_text = (
                f"🧮 *РЕЗУЛЬТАТ РОЗРАХУНКУ*\n\n"
                f"*Формат елементів:* {format_type}\n"
                f"*Кількість елементів:* {count}\n"
                f"*Тип елемента:* {battery_name}\n"
                f"*Ємність одного елемента:* {element_capacity}\n"
                f"*Вихідна ємність після перепаковки:* {total_capacity}\n\n"
                f"*ЗАГАЛЬНА ВАРТІСТЬ: {total_price} грн*\n\n"
                f"Для нового розрахунку оберіть 'Калькулятор' в головному меню."
            )
            
            bot.send_message(
                message.chat.id,
                final_text,
                reply_markup=menu.create_main_keyboard(),
                parse_mode="Markdown"
            )
            
            if user_id in menu.user_calculator:
                del menu.user_calculator[user_id]
    except Exception as e:
        logger.error(f"Error in handle_calculator_battery: {e}")

# ---------- ОБРОБНИК CALLBACK ДЛЯ КАНАЛУ ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        if call.data == "brand_dnipro":
            bot.edit_message_text(
                "🔋 *Ремонт акумуляторів*\nБренд: *Дніпро-M*\n\nОберіть модель АКБ:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=menu.create_channel_models_keyboard(),
                parse_mode="Markdown"
            )
        
        elif call.data == "show_calculator":
            bot.edit_message_text(
                "🧮 *КАЛЬКУЛЯТОР РОЗРАХУНКУ*\n\nОберіть формат елементів:",
                chat_id=chat_id,
                message_id=message_id,
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
            bot.edit_message_text(
                warranty_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=menu.create_channel_main_keyboard(),
                parse_mode="Markdown"
            )
        
        elif call.data == "shipping_payment":
            shipping_text = (
                "🚚 *ВІДПРАВКА ТА ОПЛАТА:*\n\n"
                "📦 *Варіанти відправки:*\n"
                "• Нова Пошта - 1-3 дні\n"
                "• Доставка по м.Надвірна (Безкоштовна)\n\n"
                "💳 *Оплата:* на карту перед відправкою"
            )
            bot.edit_message_text(
                shipping_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=menu.create_channel_main_keyboard(),
                parse_mode="Markdown"
            )
        
        elif call.data == "back_to_main":
            bot.edit_message_text(
                "🔋 *Ремонт акумуляторів*\n\nОберіть опцію:",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=menu.create_channel_main_keyboard(),
                parse_mode="Markdown"
            )
        
        bot.answer_callback_query(call.id)
    
    except Exception as e:
        logger.error(f"Error in handle_callback: {e}")

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
    try:
        bot.send_message(
            config.CHANNEL_ID,
            "🚀 *Бот для ремонту акумуляторів запущений!*\n\n"
            "📱 *Оберіть опцію:*",
            parse_mode="Markdown",
            reply_markup=menu.create_channel_main_keyboard()
        )
        return "✅ Пост опубліковано в канал"
    except Exception as e:
        return f"❌ Помилка: {str(e)}"

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
            time.sleep(3)
            logger.info("📢 Спроба публікації поста в канал...")
            post_to_channel()
        
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
