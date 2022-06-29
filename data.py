import sqlite3

def add_user(user_id, name, base):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    cursor.execute("INSERT INTO users(user_id, name, base) VALUES(?, ?, ?);",(user_id, name, base))
    cursor.execute("INSERT INTO categories(user_id) VALUES(?);",(user_id,))
    db.commit()

def get_info(user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    res = cursor.execute("SELECT name, day_spent, month_spend, base, base_spent, day_income, month_income FROM users WHERE user_id = ?;",(user_id,)).fetchone()
    return res

def user_exists(user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    result = cursor.execute("SELECT * FROM users WHERE user_id = ?;",(user_id,)).fetchone()
    return result

def add_to_category(user_id, amount, category=None):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    if category == None:
        money = cursor.execute("SELECT Other FROM categories WHERE user_id = ?;",(user_id,)).fetchone()
        new_money = int(money[0]) + int(amount)
        cursor.execute("UPDATE categories SET Other = ? WHERE user_id = ?;",(new_money, user_id))
    else:
        money = cursor.execute("SELECT " + category + " FROM categories WHERE user_id = ?;",(user_id,)).fetchone()
        new_money = int(money[0]) + int(amount)
        cursor.execute("UPDATE categories SET " + category +  " = ? WHERE user_id = ?;",(new_money, user_id))
    db.commit()

def add_expense(user_id, amount):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    all = cursor.execute("SELECT day_spent, month_spend, base_spent FROM users WHERE user_id = ?;",(user_id,)).fetchone()
    day_spent = int(all[0]) + int(amount)
    month_spent = int(all[1]) + int(amount)
    base_spent = int(all[2]) + int(amount)
    cursor.execute("UPDATE users SET day_spent = ? WHERE user_id = ?;",(day_spent, user_id))
    cursor.execute("UPDATE users SET month_spend = ? WHERE user_id = ?;",(month_spent, user_id))
    cursor.execute("UPDATE users SET base_spent = ? WHERE user_id = ?;",(base_spent, user_id))
    db.commit()

def get_cat_exp(user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    res = cursor.execute("SELECT * FROM categories WHERE user_id = ?;",(user_id,)).fetchone()
    expenses = [res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12], res[13]]
    return expenses

def null_days():
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    cursor.execute("UPDATE users SET day_spent = 0, day_income = 0")
    db.commit()

def null_month():
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    cursor.execute("UPDATE users SET month_spend = 0, month_income = 0")
    cursor.execute("UPDATE categories SET Products = 0, Internet = 0, Cafe = 0, Coffee = 0, House = 0, Books = 0, Lunch = 0, Transport = 0, Taxi = 0, Other = 0")
    db.commit()

def add_income(amount, user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    res = cursor.execute("SELECT day_income, month_income FROM users WHERE user_id = ?;",(user_id,)).fetchone()
    day_income = int(res[0]) + int(amount)
    month_income = int(res[1]) + int(amount)
    cursor.execute("UPDATE users SET day_income = ? WHERE user_id = ?;",(day_income, user_id))
    cursor.execute("UPDATE users SET month_income = ? WHERE user_id = ?;",(month_income, user_id))
    db.commit()

def user_exists(user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    res = cursor.execute("SELECT id FROM users WHERE user_id = ?;",(user_id,))
    return res

def get(user_id):
    db = sqlite3.connect("finance.db")
    cursor = db.cursor()
    res = cursor.execute("SELECT month_spend, month_income FROM users WHERE user_id = ?;",(user_id,)).fetchone()
    return res

