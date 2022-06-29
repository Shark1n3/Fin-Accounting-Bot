import telebot
from telebot import types
import sqlite3
import data
import time
import threading, time
import schedule
import matplotlib.pyplot as plt
import numpy as np
import os
import diagrams

from telebot.handler_backends import BaseMiddleware
from telebot.handler_backends import CancelUpdate

token = '<your token>'
bot = telebot.TeleBot(token, use_class_middlewares=True)
user = []
categories = {"Products" : ['продукты', 'еда'], "Internet" : ['интернет', 'инет'], "Cafe" : ['кафе', 'ресторан'], "Coffee" : 'кофе', "House" : ['квартплата', 'жкх'], "Books" : 'книги', "Lunch" : ['ланч', 'обед', 'столовая'], "Transport" : ['маршрутка', 'газель', 'метро', 'автобус', 'транспорт'], "Phone" : ['телефон', 'связь'], "Subs" : ['подписка', 'подписки'], "Taxi" : 'такси'}
menu_m = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_m.add('💰 Мои Траты', '📋 Траты По Категориям', '🗄 Категории', '📊 Составить Диаграмму', '❔ Помощь')

#========АНТИ СПАМ СИСТЕМА========#
class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']

    def pre_process(self, message, data):
        if not message.from_user.id in self.last_time:
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            bot.delete_message(message.chat.id, message.id)
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

        
    def post_process(self, message, data, exception):
        pass
bot.setup_middleware(SimpleMiddleware(2))
#===================================#

with sqlite3.connect("finance.db") as db:
    cursor = db.cursor()
    q = ("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name VARCHAR(50), day_spent INTEGER NOT NULL DEFAULT 0, month_spend INTEGER NOT NULL DEFAULT 0, base INTEGER NOT NULL DEFAULT 0, base_spent INTEGER NOT NULL DEFAULT 0, day_income INTEGER NOT NULL DEFAULT 0, month_income INTEGER NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, Products INTEGER NOT NULL DEFAULT 0, Internet INTEGER NOT NULL DEFAULT 0, Cafe INTEGER NOT NULL DEFAULT 0, Coffee INTEGER NOT NULL DEFAULT 0, House INTEGER NOT NULL DEFAULT 0, Books INTEGER NOT NULL DEFAULT 0, Lunch INTEGER NOT NULL DEFAULT 0, Transport INTEGER NOT NULL DEFAULT 0, Taxi INTEGER NOT NULL DEFAULT 0, Phone INTEGER NOT NULL DEFAULT 0, Subs INTEGER NOT NULL DEFAULT 0, Other INTEGER NOT NULL DEFAULT 0)""")
    cursor.executescript(q)

@bot.message_handler(commands=['start'])
def start_message(message):
    if data.user_exists(message.from_user.id == None):
     ap = bot.send_message(message.chat.id, "Привет! 👋\n\nЯ - самый удобный и умный бот финансового учёта в телеграме! Чтобы начать, введи своё имя")
     bot.register_next_step_handler(ap, enter_base)
    else:
        main_msg(message)

@bot.message_handler(commands=['menu'])
def menu(message):
     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
     markup.add('💰 Мои Траты', '📋 Траты По Категориям', '🗄 Категории', '📊 Составить Диаграмму', '❔ Помощь')
     bot.send_message(message.chat.id, "Сейчас загружу меню...", reply_markup=markup)
     main_msg(message)

def enter_base(message):
    global user
    name = message.text
    user.append(name)
    print(user)
    ix = bot.send_message(message.chat.id, "Хорошо, теперь введи сколько денег тебе *нужно* чтобы жить, это будут твои *базовые* расходы, например продукты, жилье, транспорт и т.д", parse_mode="Markdown")
    bot.register_next_step_handler(ix, all_done)

def all_done(message):
    global user, menu_m
    base = message.text
    if str(base).isdigit() == True:
     data.add_user(message.chat.id, user[0], base)
     bot.send_message(message.chat.id, "Отлично, все готово! Скоро ты сможешь пользоваться ботом...", reply_markup=menu_m)
     time.sleep(2)
     main_msg(message)
    else:
        bot.send_message(message.chat.id, "Нужно отправить число!")
        enter_base(message)

def main_msg(message):
    user_id = message.from_user.id
    base_text = ''
    inc_text = ''
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='💸 Добавить доход', callback_data='money_plus')
    markup.add(btn)
    if int(data.get_info(user_id)[4]) > int(data.get_info(user_id)[3]):
        percent = ((int(data.get_info(user_id)[4]) - int(data.get_info(user_id)[3])) / int(data.get_info(user_id)[3])) * 100
        rub = int(data.get_info(user_id)[4]) - int(data.get_info(user_id)[3])
        base_text = f"\nПревышены на {rub} рублей ({round(percent)}%)"
    if int(data.get_info(user_id)[2]) > int(data.get_info(user_id)[6]):
        percent2 = ((int(data.get_info(user_id)[2]) - int(data.get_info(user_id)[6])) / int(data.get_info(user_id)[6])) * 100
        rub2 = int(data.get_info(user_id)[2]) - int(data.get_info(user_id)[6])
        inc_text = f"\nРасходы больше доходов на {rub2} рублей ({round(percent2)}%)"
        print(inc_text)
    bot.send_message(message.chat.id, f"Здравствуй, {data.get_info(user_id)[0]} 💎\n\n💳 *Вот твои траты:*\nЗа день: {data.get_info(user_id)[1]} руб.\nЗа месяц: {data.get_info(user_id)[2]} руб.\nБазовые: {data.get_info(user_id)[4]} из {data.get_info(user_id)[3]} руб.{base_text}\n\n💵 *Вот твои доходы:*\nДоход за день: {data.get_info(user_id)[5]} руб.\nДоход за месяц: {data.get_info(user_id)[6]} руб.{inc_text}", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def text_proc(message, f=None):
    global categories
    if message.text == '💰 Мои Траты':
        main_msg(message)
    elif message.text == '❔ Помощь':
        bot.send_message(message.chat.id, "*Как добавить расход/трату?*\nЧтобы добавить трату нужно просто прислать боту сумму и категорию траты, например '250 такси'\n\n*Когда обновляются переменные трат за день и за месяц?*\nТраты за день обнуляются в 00:00 следующего дня, траты за месяц и по категориям - каждое 1-ое число нового месяца\n\nДополнительная помощь: @risely", parse_mode="Markdown")
    elif message.text == '🗄 Категории':
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text='Добавить свою категорию', callback_data='insert_categorie')
        bot.send_message(message.chat.id, "Доступные категории: \n\n•Продукты (еда, продукты)\n•Кафе (кафе, ресторан)\n•Кофе (кофе)\n•Обед (ланч, обед, столовая)\n•Общ.транспорт (автобус, метро, маршрутка, газель, транспорт)\n•Интернет (интернет, инет)\n•Связь (телефон, связь)\n•Подписки (подписка, подписки)\n•Такси\n•Прочее\n\nТы можешь также добавить свою категорию и она появится в списке", reply_markup=markup)
    elif message.text == '📋 Траты По Категориям':
        exp = data.get_cat_exp(message.from_user.id)
        print(exp)
        bot.send_message(message.chat.id, f"Вот твои *траты по категориям*: \n\n🥦 Продукты: *{exp[0]}* руб.\n🌭 Кафе: *{exp[2]}* руб.\n🌍 Интернет: *{exp[1]}* руб.\n☕️ Кофе: *{exp[3]}* руб.\n🥣 Обед: {exp[6]} руб.\n🚍 Общ.Транспорт: *{exp[7]}* руб.\n📝 Квартплата: *{exp[4]}* руб.\n📖 Книги: *{exp[5]}* руб.\n☎️ Связь: *{exp[9]}* руб.\n💳 Подписки: *{exp[10]}* руб.\n🚖 Такси: *{exp[8]}* руб.\n🌀 Прочее: *{exp[11]}* руб.", parse_mode="Markdown")
    elif message.text == '📊 Составить Диаграмму':
        if f == 'id':
            return message.from_user.id
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Расходы по категориям', callback_data='diagr1')
        btn2 = types.InlineKeyboardButton(text='Доходы к расходам', callback_data='diagr2')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Выбери какую диаграмму нужно построить:", reply_markup=markup)
    else:
        try:
         array = str(message.text).split()
         if str(array[0]).isdigit() == True and array.__len__() == 1:
           amount = array[0]
           bot.send_message(message.chat.id, f"Расход в {amount} рублей добавлен в 'Прочее'")
           data.add_to_category(message.from_user.id, amount)
           data.add_expense(message.from_user.id, amount)
         else:
            amount = array[0]
            categorie = array[1]
            for key, value in categories.items():
              if categorie in value:
                print(key)
                bot.send_message(message.chat.id, f"Добавлен расход {amount} рублей на {categorie}")
                data.add_to_category(message.from_user.id, amount, key)
                data.add_expense(message.from_user.id, amount)
        except IndexError:
            bot.send_message(message.chat.id, "Введенный текст не распознан. Если *хотите добавить трату*, напишите так, пример: *'250 такси'* или *'500 продукты'*, если ввести просто цифру, трата автоматически определится в категорию 'Прочее'", parse_mode="Markdown")

@bot.callback_query_handler(func= lambda call: True)
def call(call):
    if call.data == 'money_plus':
        ue = bot.send_message(call.message.chat.id, "Введи сумму, которую хочешь добавить в доходы")
        bot.register_next_step_handler(ue, add_money)
    elif call.data == 'diagr1':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Ваша диаграмма создается...\nЭто может занять несколько секунд')
        round_1(call.message, call.from_user.id)
    elif call.data == 'diagr2':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Ваша диаграмма создается...\nЭто может занять несколько секунд')
        round_2(call.message, call.from_user.id)

def round_1(message, user_id):
    diagrams.diagr1(user_id)
    if diagrams.diagr1(user_id) == False:
        bot.send_message(message.chat.id, "Для составления диаграммы не хватает данных")
    else:
        photo = open(f'{user_id}_cat_exp.png', 'rb')
        bot.send_photo(chat_id=message.chat.id, photo=photo, caption='Вот твоя диаграмма расходов по категориям')

def round_2(message, user_id):
    diagrams.diagr2(user_id)
    if diagrams.diagr2(user_id) == False:
        bot.send_message(message.chat.id, "Для составления диаграммы не хватает данных.")
    else:
        photo = open(f'{user_id}_exp_inc.png', 'rb')
        bot.send_photo(chat_id=message.chat.id, photo=photo, caption='Вот твоя диаграмма расходов к доходам')

def add_money(message):
    data.add_income(message.text, message.from_user.id)
    bot.send_message(message.chat.id, f"Добавлен доход в {message.text} рублей")

import schedule
import data

def days_nulling():
    data.null_days()
    print('Days nulled')

def month_nulling():
    data.null_month()
    print('Months was nulled successfully')

if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    schedule.every().day.at('00:00').do(days_nulling)
    schedule.every(30).days.do(month_nulling)
    while True:
        schedule.run_pending()
        time.sleep(1)
