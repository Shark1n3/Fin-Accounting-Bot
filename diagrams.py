import matplotlib.pyplot as plt
import numpy as np
import data
import bot

def diagr1(user_id):
   try:
    cates = data.get_cat_exp(user_id)
    cats = {'Продукты' : cates[0], 'Интернет' : cates[1], 'Кафе' : cates[2], 'Кофе' : cates[3], 'Книги' : cates[5], 'Дом' : cates[4], 'Обед' : cates[6], 'Транспорт' : cates[7], 'Подписки' : cates[8], 'Связь' : cates[9], 'Такси' : cates[10], 'Прочее' : cates[11]}
    values = {}
    for key, value in cats.items():
        if value != 0:
            values[key] = value
    plt.title('Расходы по категориям')
    plt.figure()
    plt.bar(values.keys(), values.values())
    plt.savefig(f'{user_id}_cat_exp.png')
   except:
    return False

def diagr2(user_id):
    result = data.get(user_id)
    if result[0] == 0 or result[1] == 0:
        return False
    else:
        date = [result[0], result[1]]
        labels = ['Расход', 'Доход']
        plt.title('Доходы к расходам')
        plt.figure()
        plt.pie(date, labels=labels, autopct='%.1f%%')
        plt.savefig(f'{user_id}_exp_inc.png')