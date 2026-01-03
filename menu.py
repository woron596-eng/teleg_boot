from telebot import types

# ---------- ГЛОБАЛЬНІ ЗМІННІ ----------
user_selection = {}
user_calculator = {}

# ---------- КЛАВІАТУРИ ----------
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add("Дніпро-M", "Калькулятор", "Гарантія", "Відправка та оплата")
    return keyboard

def create_models_keyboard():
    from config import MODELS_STRUCTURE
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = list(MODELS_STRUCTURE.keys())
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.add("◀️ Назад")
    return keyboard

def create_battery_type_keyboard(model_key):
    from config import MODELS_STRUCTURE
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    batteries = MODELS_STRUCTURE[model_key]["batteries"]
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
    from config import CALCULATOR_DATA
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    counts = list(CALCULATOR_DATA[format_type]["prices"].keys())
    
    for i in range(0, len(counts), 3):
        row = counts[i:i+3]
        keyboard.add(*row)
    
    keyboard.add("◀️ Назад до вибору формату")
    return keyboard

def create_calculator_battery_keyboard(format_type, count):
    from config import CALCULATOR_DATA
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    prices_for_count = CALCULATOR_DATA[format_type]["prices"][count]
    
    for battery_name, total_price in prices_for_count.items():
        button_text = f"{battery_name} - {total_price} грн"
        keyboard.add(button_text)
    
    keyboard.add("◀️ Назад до кількості")
    return keyboard

# ---------- INLINE КЛАВІАТУРИ ДЛЯ КАНАЛУ ----------
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
    from config import MODELS_STRUCTURE
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for model in MODELS_STRUCTURE:
        buttons.append(types.InlineKeyboardButton(model, callback_data=f"model_{model}"))
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])
    
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_channel_battery_keyboard(model_key):
    from config import MODELS_STRUCTURE
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    batteries = MODELS_STRUCTURE[model_key]["batteries"]
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
    from config import CALCULATOR_DATA
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    counts = list(CALCULATOR_DATA[format_type]["prices"].keys())
    
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
