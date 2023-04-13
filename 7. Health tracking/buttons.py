from database import cursor, database
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

page = 1

def menu(bot, callback):
    cursor.execute("""SELECT user_id from health""")
    user = cursor.fetchall()
    users = []
    for i in user:
        users.append(i[0])
    if callback.chat.id not in users:
        markup=InlineKeyboardMarkup(row_width=3)
        item1 = InlineKeyboardButton(text = "Заполнить", callback_data = "add")
        markup.add(item1)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)
    else:
        markup=InlineKeyboardMarkup(row_width=3)
        item2 = InlineKeyboardButton(text = "Удалить", callback_data = "del")
        item3 = InlineKeyboardButton(text = "Обновить", callback_data = "update")
        item5 = InlineKeyboardButton(text = "Состояние здоровья", callback_data = "health")
        markup.add(item5, item3)
        markup.add(item2)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)

# callback
def mycallback(bot, callback):
    if callback.data == 'add':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши свой вес: ',  parse_mode='html', reply_markup=keyboard)

        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши на своё давление: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add2)
            
        def add2(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши свою частоту сердечных сокращений: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add3)
            
        def add3(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            us_id = message.from_user.id
            cursor.execute('INSERT INTO health (user_id, weight, blood_pressure, heart_rate) VALUES (?, ?, ?, ?)', (us_id, a[1], a[0], a[2]))
            database.commit()
            bot.send_message(callback.message.chat.id, text = f'Я добавил твои данные в базу данных: \n{a}', parse_mode='markdown')
            menu(bot, callback.message)
        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'del':
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        cursor.execute(f"""DELETE FROM health WHERE user_id = {callback.message.chat.id}""")
        database.commit()
        menu(bot, callback.message)

    elif callback.data == 'update':
        markup=InlineKeyboardMarkup(row_width=4)
        item1 = InlineKeyboardButton(text = "Вес", callback_data = "weight")
        item2 = InlineKeyboardButton(text = "Давление", callback_data = "blood_pressure")
        item3 = InlineKeyboardButton(text = "Пульс", callback_data = "heart_rate")
        back = InlineKeyboardButton(text = "Выйти", callback_data = "close")
        markup.add(item1, item2, item3)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)

    elif callback.data == 'health':
        cursor.execute(f'''SELECT * FROM health WHERE user_id = {callback.message.chat.id}''')
        health = cursor.fetchall()
        for i in health:
            bot.send_message(callback.message.chat.id, text = 
            (
            f'Вес: {(i[2])} Кг\n'
            f'Давление: {(i[3])}\n'
            f'Ритм: {(i[4])}\n'
            ))
            bot.answer_callback_query(callback_query_id=callback.id, show_alert=False)

    elif callback.data == 'close':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        menu(bot, callback.message)

    elif callback.data == 'weight':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши свой вес: ', reply_markup=keyboard)
        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            weight = a[0]
            id = callback.message.chat.id
            cursor.execute(f"""UPDATE health SET weight = ? WHERE user_id = ?""", (weight, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я изменил твой вес на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'blood_pressure':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши своё давление: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            blood_pressure = a[0]
            id = callback.message.chat.id
            cursor.execute(f"""UPDATE health SET blood_pressure = ? WHERE user_id = ?""", (blood_pressure, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я изменил твоё давление на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'heart_rate':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши свой сердечный ритм: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            heart_rate = a[0]
            id = callback.message.chat.id
            cursor.execute(f"""UPDATE health SET heart_rate = ? WHERE user_id = ?""", (heart_rate, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я изменил твой сердечный ритм на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)
