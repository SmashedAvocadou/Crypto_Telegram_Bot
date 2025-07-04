import requests
import telebot
from telebot import types
from datetime import datetime, timedelta
import time
import webbrowser
import os
from dotenv import load_dotenv
load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN_BOT'))
BINANCE_URL = "https://api.binance.com/api/v3"
EXCHANGE_API= os.getenv('API_TOKEN')

user_currency= {}


@bot.message_handler(commands=['start'])
def choose_currency(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['USDT', 'EUR', 'RUB']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(message.chat.id, "Choose currency:", reply_markup=markup)



@bot.message_handler(func=lambda msg: msg.text in ['USDT', 'EUR', 'RUB'])
def show_crypto(message):
    user_currency[message.chat.id] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['BTC', 'ETH', 'XRP', 'SOL', 'BNB', 'TRX', 'DOGE', 'ADA', 'TON', 'XLM', 'SUI', 'HYPER', 'AVAX', 'LTC', 'XMR', 'HBAR', 'DOT', 'PEPE', 'APT', 'LINK']
    buttons.append('🔄 Change currency')
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(message.chat.id, f"Choose cryptocurrency:", reply_markup=markup)




def get_price_usdt(symbol):
    symbol = symbol.upper()
    if symbol.endswith('EUR') or symbol.endswith('RUB'):
        symbol = symbol[0:-3]
    if not symbol.endswith('USDT'):
        pair = symbol + 'USDT'
    else:
        pair = symbol
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={pair}'
    req = requests.get(url)
    data = req.json()

    if 'price' in data:
        return float(data['price'])
    else:
        print(f"❌ Binance error: {data}, {pair}")
        return None

@bot.message_handler(func=lambda msg: msg.text == 'EUR' )
def get_usdt_to_eur():
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API}/pair/USD/EUR'
    req = requests.get(url)
    data = req.json()

    if data['result'] == 'success':
        return data['conversion_rate']
    else:
        print("Ошибка при получении курса USDT→EUR")
        return None


def get_crypto_price_eur(symbol):
    price_usdt = get_price_usdt(symbol)
    eur_rate = get_usdt_to_eur()
    if eur_rate:
        return price_usdt * eur_rate
    else:
        return None

@bot.message_handler(func=lambda msg: msg.text == 'RUB' )
def get_usdt_to_rub():
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API}/pair/USD/RUB'
    req = requests.get(url)
    data = req.json()

    if data['result'] == 'success':
        return data['conversion_rate']
    else:
        print("Ошибка при получении курса USDT→RUB")
        return None


def get_crypto_price_rub(symbol):
    price_usdt = get_price_usdt(symbol)
    rub_rate = get_usdt_to_rub()
    if rub_rate:
        return price_usdt * rub_rate
    else:
        return None





@bot.message_handler(func=lambda msg: msg.text == '🔄 Change currency' )
def change_currency(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('USDT'), types.KeyboardButton('EUR'), types.KeyboardButton('RUB'))
    bot.send_message(message.chat.id, 'Choose currency:', reply_markup=markup)



def get_price(symbol):
    response = requests.get(f'{BINANCE_URL}/ticker/price', params={"symbol": symbol})
    return float(response.json()['price'])


def get_old_price(symbol, days_ago):
    end_time = int(time.time() * 1000)
    start_time = int((datetime.now() - timedelta(days=days_ago)).timestamp() * 1000)

    response = requests.get(f"{BINANCE_URL}/klines", params={
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1
    })

    data = response.json()
    if data:
        open_price = float(data[0][1])
        return open_price
    else:
        return None




@bot.message_handler(func=lambda message: message.text in ['BTC', 'ETH', 'XRP', 'SOL', 'BNB', 'TRX', 'DOGE', 'ADA', 'TON', 'XLM', 'SUI', 'HYPER', 'AVAX', 'LTC', 'XMR', 'HBAR', 'DOT', 'PEPE', 'APT', 'LINK'])
def show_price_crypto(message):
    currency = user_currency.get(message.chat.id, 'USDT')
    if currency == 'EUR':
        try:
            symbol = message.text.upper() + 'EUR'
            symbol_without_currency = message.text.upper()
            current = get_price(symbol)

            # Создаю inline кнопки для интервалов/ Creating inline buttons for intervals
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📉 3 days", callback_data=f"{symbol}_3"),
                types.InlineKeyboardButton("📉 7 days", callback_data=f"{symbol}_7"),
                types.InlineKeyboardButton("📉 Month", callback_data=f"{symbol}_30"),
            )
            markup.add(
                types.InlineKeyboardButton("📉 Year", callback_data=f"{symbol}_365"),
                types.InlineKeyboardButton("📉 2 Years", callback_data=f"{symbol}_730"),
                types.InlineKeyboardButton("📉 3 Years", callback_data=f"{symbol}_1095"),
            )
            bot.send_message(message.chat.id, f"💰 Price now {symbol_without_currency}: {current} EUR", reply_markup=markup)
        except Exception as e:
            symbol = message.text.upper() + 'EUR'
            symbol_without_currency = message.text.upper()
            price_in_euros = get_crypto_price_eur(symbol)
            if price_in_euros:
                bot.send_message(message.chat.id,
                                 f"💰 Price now {symbol_without_currency}: <b><u>{price_in_euros}</u></b> EUR. <i>No history available</i>.", parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, f"❌ Can't fetch price now.{e}")

    elif currency == 'RUB':
        try:
            symbol = message.text.upper() + 'RUB'
            symbol_without_currency = message.text.upper()
            current = get_price(symbol)

            # Создаю inline кнопки для интервалов/ Creating inline buttons for intervals
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📉 3 days", callback_data=f"{symbol}_3"),
                types.InlineKeyboardButton("📉 7 days", callback_data=f"{symbol}_7"),
                types.InlineKeyboardButton("📉 Month", callback_data=f"{symbol}_30"),
            )
            markup.add(
                types.InlineKeyboardButton("📉 Year", callback_data=f"{symbol}_365"),
                types.InlineKeyboardButton("📉 2 Years", callback_data=f"{symbol}_730"),
                types.InlineKeyboardButton("📉 3 Years", callback_data=f"{symbol}_1095"),
            )
            bot.send_message(message.chat.id, f"💰 Price now {symbol_without_currency}: {current} RUB", reply_markup=markup)
        except Exception as e:
            symbol = message.text.upper() + 'RUB'
            symbol_without_currency = message.text.upper()
            price_in_rubles = get_crypto_price_rub(symbol)
            if price_in_rubles:
                bot.send_message(message.chat.id, f"💰 Price now {symbol_without_currency}: <b><u>{price_in_rubles}</u></b> RUB. <i>No history available</i>.", parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, f"❌ Can't fetch price now.{e}")
    else:
        symbol = message.text.upper() + 'USDT'
        symbol_without_currency = message.text.upper()
        current = get_price(symbol)

        # Создаю inline кнопки для интервалов/ Creating inline buttons for intervals
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📉 3 days", callback_data=f"{symbol}_3"),
            types.InlineKeyboardButton("📉 7 days", callback_data=f"{symbol}_7"),
            types.InlineKeyboardButton("📉 Month", callback_data=f"{symbol}_30"),
        )
        markup.add(
            types.InlineKeyboardButton("📉 Year", callback_data=f"{symbol}_365"),
            types.InlineKeyboardButton("📉 2 Years", callback_data=f"{symbol}_730"),
            types.InlineKeyboardButton("📉 3 Years", callback_data=f"{symbol}_1095"),
        )
        bot.send_message(message.chat.id, f"💰 Price now {symbol_without_currency}: {current} USDT", reply_markup=markup)


# Обработка нажатия на кнопку сравнения
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    currency = user_currency.get(call.message.chat.id, 'USDT')
    if currency == 'EUR':
        data = call.data  # Пример: BTCEUR_7
        symbol, days = data.split('_')
        days = int(days)

        now = get_price(symbol)
        old = get_old_price(symbol, days)

        if old:
            diff = now - old
            percent = (diff / old) * 100
            arrow = "🔺" if diff > 0 else "🔻"
            bot.send_message(call.message.chat.id,
                             f"{symbol}\n"
                             f"📆 {days} days ago: {old:.2f} EUR\n"
                             f"📈 Now: {now:.2f} EUR\n"
                             f"{arrow} Alteration: {diff:.2f} EUR ({percent:.2f}%)")
        else:
            bot.send_message(call.message.chat.id, "❌ Error.")

    elif currency == 'RUB':
        data = call.data  # Пример: BTCRUB_7
        symbol, days = data.split('_')
        days = int(days)

        now = get_price(symbol)
        old = get_old_price(symbol, days)

        if old:
            diff = now - old
            percent = (diff / old) * 100
            arrow = "🔺" if diff > 0 else "🔻"
            bot.send_message(call.message.chat.id,
                             f"{symbol}\n"
                             f"📆 {days} days ago: {old:.2f} RUB\n"
                             f"📈 Now: {now:.2f} RUB\n"
                             f"{arrow} Alteration: {diff:.2f} RUB ({percent:.2f}%)")
        else:
            bot.send_message(call.message.chat.id, "❌ Error.")

    else:
        data = call.data  # Пример: BTCUSDT_7
        symbol, days = data.split('_')
        days = int(days)

        now = get_price(symbol)
        old = get_old_price(symbol, days)

        if old:
            diff = now - old
            percent = (diff / old) * 100
            arrow = "🔺" if diff > 0 else "🔻"
            bot.send_message(call.message.chat.id,
                             f"{symbol}\n"
                             f"📆 {days} days ago: {old:.2f} USDT\n"
                             f"📈 Now: {now:.2f} USDT\n"
                             f"{arrow} Alteration: {diff:.2f} USDT ({percent:.2f}%)")
        else:
            bot.send_message(call.message.chat.id, "❌ Error.")





@bot.message_handler(commands=['help'])
def info(message):
    bot.send_message(message.chat.id,'Choose crypto and then choose period of the time you would like to see')


@bot.message_handler(commands=['website'])
def web(message):
    webbrowser.open('https://www.binance.com')




bot.polling(none_stop=True)