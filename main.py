import telebot
from currency_converter import CurrencyConverter
from telebot import types
import sys
import requests
import requests
from bs4 import BeautifulSoup as bs
import re
from dateutil.parser import parse

bot = telebot.TeleBot('6736692677:AAFLu-4SrE-rvh2WgrCliGvoSWCP7QaaXCI')
currency = CurrencyConverter()
amount = 0


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Введите сумму')
    bot.register_next_step_handler(message, summa)

def convert_currency_xe(src, dst, amount):
    def get_digits(text):
        """Returns the digits and dots only from an input text as a float
        Args:
            text (str): Target text to parse
        """
        new_text = ""
        for c in text:
            if c.isdigit() or c == ".":
                new_text += c
        return float(new_text)

    url = f"https://www.xe.com/currencyconverter/convert/?Amount={amount}&From={src}&To={dst}"
    content = requests.get(url).content
    soup = bs(content, "html.parser")
    exchange_rate_html = soup.find_all("p")[2]
    # get the last updated datetime
    last_updated_datetime = parse(re.search(r"Last updated (.+)", exchange_rate_html.parent.parent.find_all("div")[-2].text).group()[12:])
    return last_updated_datetime, get_digits(exchange_rate_html.text)
def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат. Впишите сумму')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('RUB/USD', callback_data='rub/usd')
        btn2 = types.InlineKeyboardButton('USD/RUB', callback_data='usd/rub')
        btn3 = types.InlineKeyboardButton('RUB/EUR', callback_data='rub/eur')
        btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Число должно быть больше 0. Впишите сумму')
        bot.register_next_step_handler(message, summa)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        source_currency = values[0]
        destination_currency = values[1]
        last_updated_datetime, exchange_rate = convert_currency_xe(source_currency, destination_currency, amount)
        print("Last updated datetime:", last_updated_datetime)
        print(f"{amount} {source_currency} = {exchange_rate} {destination_currency}")
        bot.send_message(call.message.chat.id, f'Получается: {round(exchange_rate, 2)}.\nМожете заново вводить число')
        bot.register_next_step_handler(call.message, summa)
        print(values)
        print(amount)
    else:
        bot.send_message(call.message.chat.id, 'Введите значения (1/2)')
        bot.register_next_step_handler(call.message, mycurrency)

def mycurrency(message):
    values = message.text.upper().split('/')
    source_currency = values[0]
    destination_currency = values[1]
    last_updated_datetime, exchange_rate = convert_currency_xe(source_currency, destination_currency, amount)
    print("Last updated datetime:", last_updated_datetime)
    print(f"{amount} {source_currency} = {exchange_rate} {destination_currency}")
    bot.send_message(message.chat.id, f'Получается: {round(exchange_rate, 2)}.\nМожете заново вводить число')
    bot.register_next_step_handler(message, summa)
    print(values)
    print(amount)


bot.polling(none_stop=True)