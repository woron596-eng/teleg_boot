import os

# ==================== КОНФІГУРАЦІЯ ====================
TOKEN = "8252548275:AAF0qYbEZCoBPEN6gNHx2kkYi9gHoUPNKrA"
CHANNEL_ID = "@tester_avto"

# Налаштування для Webhook
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
if not WEBHOOK_URL:
    print("⚠️ УВАГА: RENDER_EXTERNAL_URL не встановлено!")
    WEBHOOK_URL = "https://telegram-battery-bot-ga5p.onrender.com"

# ---------- ДАНІ ДЛЯ КАЛЬКУЛЯТОРА ----------
CALCULATOR_DATA = {
    "18650": {
        "element_capacity": "3000mAh",
        "prices": {
            "2шт": {
                "Ampace JP30 36А": 700,
                "EVE 30P 20A": 550,
                "DMEGC 30P 20A": 550
            },
            "3шт": {
                "Ampace JP30 36А": 850,
                "EVE 30P 20A": 700,
                "DMEGC 30P 20A": 700
            },
            "4шт": {
                "Ampace JP30 36А": 1100,
                "EVE 30P 20A": 800,
                "DMEGC 30P 20A": 800
            },
            "5шт": {
                "Ampace JP30 36А": 1250,
                "EVE 30P 20A": 900,
                "DMEGC 30P 20A": 900
            },
            "6шт": {
                "Ampace JP30 36А": 1400,
                "EVE 30P 20A": 1150,
                "DMEGC 30P 20A": 1150
            },
            "10шт": {
                "Ampace JP30 36А": 2000,
                "EVE 30P 20A": 1600,
                "DMEGC 30P 20A": 1600
            },
            "12шт": {
                "Ampace JP30 36А": 2450,
                "EVE 30P 20A": 1800,
                "DMEGC 30P 20A": 1800
            },
            "15шт": {
                "Ampace JP30 36А": 2900,
                "EVE 30P 20A": 2100,
                "DMEGC 30P 20A": 2100
            },
            "20шт": {
                "Ampace JP30 36А": 3800,
                "EVE 30P 20A": 2800,
                "DMEGC 30P 20A": 2800
            }
        },
        "total_capacity": {
            "2шт": "3Ah",
            "3шт": "3Ah",
            "4шт": "3Ah",
            "5шт": "3Ah",
            "6шт": "3Ah",
            "10шт": "6Ah",
            "12шт": "6Ah",
            "15шт": "9Ah",
            "20шт": "12Ah"
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

# ДАНІ З ВИХІДНОЮ ЄМНІСТЮ (для Дніпро-M)
MODELS_STRUCTURE = {
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
