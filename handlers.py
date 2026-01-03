import logging
from telebot import types
import menu
import config

logger = logging.getLogger(__name__)

# ---------- ОБРОБНИКИ ПОВІДОМЛЕНЬ ----------
def handle_start(bot, message):
    try:
        bot.send_message(
            message.chat.id,
            "Ремонт акумуляторів\n\nОберіть опцію:",
            reply_markup=menu.create_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")

def handle_messages(bot, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Головне меню
        if text == "Дніпро-M":
            menu.user_selection[user_id] = {'brand': 'Дніпро-M'}
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                reply_markup=menu.create_models_keyboard()
            )
        
        elif text == "Калькулятор":
            menu.user_calculator[user_id] = {'step': 'format'}
            bot.send_message(
                chat_id,
                "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
                "**Оберіть формат елементів:**",
                reply_markup=menu.create_calculator_format_keyboard(),
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
            bot.send_message(chat_id, warranty_text, reply_markup=menu.create_main_keyboard())
        
        elif text == "Відправка та оплата":
            shipping_text = (
                "🚚 ВІДПРАВКА ТА ОПЛАТА:\n\n"
                "📦 Варіанти відправки:\n"
                "• Нова Пошта - 1-3 дні\n"
                "• Доставка по м.Надвірна(Безкоштовна)\n\n"
                "💳 Оплата на карту перед відправкою:\n"
                "• Стандартний ремонт - 1-3 дні\n"
            )
            bot.send_message(chat_id, shipping_text, reply_markup=menu.create_main_keyboard())
        
        # Обробка кнопки "Назад"
        elif text == "◀️ Назад":
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\n\nОберіть опцію:",
                reply_markup=menu.create_main_keyboard()
            )
        
        elif text == "◀️ Назад до моделей":
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                reply_markup=menu.create_models_keyboard()
            )
        
        elif text == "◀️ Назад до типів АКБ":
            if user_id in menu.user_selection and 'model' in menu.user_selection[user_id]:
                model = menu.user_selection[user_id]['model']
                bot.send_message(
                    chat_id,
                    f"Ремонт акумуляторів\nМодель: {model}\n\nОберіть тип акумулятора:",
                    reply_markup=menu.create_battery_type_keyboard(model)
                )
            else:
                bot.send_message(
                    chat_id,
                    "Ремонт акумуляторів\nБренд: Дніпро-M\n\nОберіть модель АКБ:",
                    reply_markup=menu.create_models_keyboard()
                )
        
        elif text == "◀️ Назад до вибору формату":
            menu.user_calculator[user_id] = {'step': 'format'}
            bot.send_message(
                chat_id,
                "🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                "Розберіть акумулятор, порахуйте кількість елементів та визначте їх формат:\n\n"
                "**Оберіть формат елементів:**",
                reply_markup=menu.create_calculator_format_keyboard(),
                parse_mode="Markdown"
            )
        
        elif text == "◀️ Назад до кількості":
            if user_id in menu.user_calculator and 'format' in menu.user_calculator[user_id]:
                format_type = menu.user_calculator[user_id]['format']
                bot.send_message(
                    chat_id,
                    f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                    f"**Формат:** {format_type}\n"
                    f"**Ємність одного елемента:** {config.CALCULATOR_DATA[format_type]['element_capacity']}\n\n"
                    f"**Оберіть кількість елементів:**",
                    reply_markup=menu.create_calculator_count_keyboard(format_type),
                    parse_mode="Markdown"
                )
        
        # Обробка вибору формату для калькулятора
        elif text in ["18650", "21700"]:
            if user_id not in menu.user_calculator:
                menu.user_calculator[user_id] = {}
            menu.user_calculator[user_id]['format'] = text
            menu.user_calculator[user_id]['step'] = 'count'
            
            bot.send_message(
                chat_id,
                f"🧮 **КАЛЬКУЛЯТОР РОЗРАХУНКУ**\n\n"
                f"**Формат:** {text}\n"
                f"**Ємність одного елемента:** {config.CALCULATOR_DATA[text]['element_capacity']}\n\n"
                f"**Оберіть кількість елементів:**",
                reply_markup=menu.create_calculator_count_keyboard(text),
                parse_mode="Markdown"
            )
        
        # Обробка вибору кількості елементів для калькулятора
        elif text.endswith("шт") and text[:-2].isdigit():
            if user_id in menu.user_calculator and 'format' in menu.user_calculator[user_id]:
                format_type = menu.user_calculator[user_id]['format']
                count = text
                
                if count in config.CALCULATOR_DATA[format_type]["prices"]:
                    menu.user_calculator[user_id]['count'] = count
                    menu.user_calculator[user_id]['step'] = 'battery'
                    
                    total_capacity = config.CALCULATOR_DATA[format_type]["total_capacity"][count]
                    prices_for_count = config.CALCULATOR_DATA[format_type]["prices"][count]
                    
                    if format_type == "18650":
                        elements_text = "**Для 18650:**\n"
                        for battery_name, total_price in prices_for_count.items():
                            elements_text += f"• {battery_name} - {total_price} грн\n"
                    else:
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
                        reply_markup=menu.create_calculator_battery_keyboard(format_type, count),
                        parse_mode="Markdown"
                    )
        
        # Обробка вибору типу елемента для калькулятора
        elif " - " in text and " грн" in text and user_id in menu.user_calculator and menu.user_calculator[user_id].get('step') == 'battery':
            parts = text.split(" - ")
            battery_name = parts[0].strip()
            total_price_str = parts[1].replace(" грн", "").strip()
            total_price = int(total_price_str)
            
            if user_id in menu.user_calculator and 'format' in menu.user_calculator[user_id] and 'count' in menu.user_calculator[user_id]:
                format_type = menu.user_calculator[user_id]['format']
                count = menu.user_calculator[user_id]['count']
                
                total_capacity = config.CALCULATOR_DATA[format_type]["total_capacity"][count]
                element_capacity = config.CALCULATOR_DATA[format_type]["element_capacity"]
                
                final_text = (
                    f"🧮 **РЕЗУЛЬТАТ РОЗРАХУНКУ**\n\n"
                    f"**Формат елементів:** {format_type}\n"
                    f"**Кількість елементів:** {count}\n"
                    f"**Тип елемента:** {battery_name}\n"
                    f"**Ємність одного елемента:** {element_capacity}\n"
                    f"**Вихідна ємність після перепаковки:** {total_capacity}\n\n"
                    f"**ЗАГАЛЬНА ВАРТІСТЬ: {total_price} грн**\n\n"
                    f"Для нового розрахунку оберіть 'Калькулятор' в головному меню."
                )
                
                bot.send_message(
                    chat_id,
                    final_text,
                    reply_markup=menu.create_main_keyboard(),
                    parse_mode="Markdown"
                )
                
                if user_id in menu.user_calculator:
                    del menu.user_calculator[user_id]
        
        # Обробка вибору моделі (Дніпро-M)
        elif text in config.MODELS_STRUCTURE:
            menu.user_selection[user_id] = {'model': text}
            model_data = config.MODELS_STRUCTURE[text]
            bot.send_message(
                chat_id,
                f"Ремонт акумуляторів\n"
                f"🔋 Модель: {text}\n"
                f"⚡ Напруга: {model_data.get('voltage', 'Н/Д')}\n"
                f"📊 Вихідна ємність: {model_data['capacity']}\n"
                f"🔧 Тип: {model_data['type']}\n\n"
                f"Оберіть тип акумулятора:",
                reply_markup=menu.create_battery_type_keyboard(text)
            )
        
        # Обробка вибору типу акумулятора (Дніпро-M)
        elif " - " in text and " грн" in text and user_id in menu.user_selection and 'model' in menu.user_selection[user_id]:
            parts = text.split(" - ")
            battery_name = parts[0].strip()
            battery_price = parts[1].replace(" грн", "").strip()
            
            if user_id in menu.user_selection and 'model' in menu.user_selection[user_id]:
                model_key = menu.user_selection[user_id]['model']
                
                battery_capacity = ""
                for name, capacity, price in config.MODELS_STRUCTURE[model_key]["batteries"]:
                    if name == battery_name:
                        battery_capacity = capacity
                        break
                
                menu.user_selection[user_id]['battery_type'] = battery_name
                menu.user_selection[user_id]['battery_capacity'] = battery_capacity
                menu.user_selection[user_id]['price'] = int(battery_price)
                
                bot.send_message(
                    chat_id,
                    f"✅ Ви обрали:\n\n"
                    f"🔋 Модель: {menu.user_selection[user_id]['model']}\n"
                    f"⚡ Тип акумулятора: {battery_name}\n"
                    f"📊 Вихідна ємність: {battery_capacity}\n"
                    f"💰 Ціна: {battery_price} грн\n\n"
                    f"Тепер оберіть кількість акумуляторів:",
                    reply_markup=menu.create_count_keyboard()
                )
        
        # Обробка вибору кількості (Дніпро-M)
        elif text.isdigit() and 1 <= int(text) <= 10 and user_id in menu.user_selection and 'battery_type' in menu.user_selection[user_id]:
            count = int(text)
            model = menu.user_selection[user_id]['model']
            battery_type = menu.user_selection[user_id]['battery_type']
            battery_capacity = menu.user_selection[user_id]['battery_capacity']
            price_per = menu.user_selection[user_id]['price']
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
                reply_markup=menu.create_main_keyboard()
            )
            if user_id in menu.user_selection:
                del menu.user_selection[user_id]
        
        else:
            bot.send_message(
                chat_id,
                "Ремонт акумуляторів\n\nОберіть опцію:",
                reply_markup=menu.create_main_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")
