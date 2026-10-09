import requests
import telebot
import os
from dotenv import load_dotenv
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))


def load_prices():
    # Binance без параметра symbol отдаёт цены ВСЕХ пар (больше 2000)
    data = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=10).json()
    return sorted(data, key=lambda x : x["symbol"])  # для бинарного поиска нужна сортировка


def top_volume():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    data = requests.get(url, timeout=10).json()
    data = sorted(data, key=lambda x: float(x["quoteVolume"]), reverse=True)[:5]
    return data



def linear_search(items, symbol):
    steps = 0
    for item in items:
        steps += 1
        if item["symbol"] == symbol:
            return item, steps
    return None, steps


def binary_search(items, symbol):
    steps = 0
    left, right = 0, len(items) - 1
    while left <= right:
        steps += 1
        mid = (left + right) // 2
        current = items[mid]["symbol"]
        if current == symbol:
            return items[mid], steps
        if current < symbol:
            left = mid + 1
        else:
            right = mid - 1
    return None, steps



@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m,
    "👋 Привет! Я бот для поиска цен криптовалют на Binance.\n"
    "Доступные функции:\n"
    "/top - топ пар по бьемам"
    "/search — найти торговую пару и её цену\n"
    "Пример:\n"
    "/search ETH/USDT\n"
    "Также я сравниваю время поиска:\n"
    "🔹 Линейный поиск\n"
    "🔹 Бинарный поиск"
    )

@bot.message_handler(commands=["top"])
def top(message):
    data = top_volume()
    text = "Топ 5 пар по объёму:\n\n"
    for i in range(5):
        text += f"{i + 1}. {data[i]['symbol']} — {data[i]['quoteVolume']}\n"
    bot.reply_to(message, text)


@bot.message_handler(commands=["search"])
def search(m):
    args = m.text.split()[1:]
    if not args:
        bot.reply_to(m, "Пример: /search ETH/USDT")
        return

    symbol = args[0].upper().replace("/", "")
    items = load_prices()
    item1, steps1 = linear_search(items, symbol)
    (item2, steps2) = binary_search(items, symbol)

    if item1 is None:
        bot.reply_to(m, "Пара не найдена")
        return

    bot.reply_to(
        m,
        f"{symbol}: {item1['price']}\n\n"
        f"Всего пар: {len(items)}\n"
        f"Линейный поиск: {steps1} шагов\n"
        f"Бинарный поиск: {steps2} шагов",
    )


bot.infinity_polling()
