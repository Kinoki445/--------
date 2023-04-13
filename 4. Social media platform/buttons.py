from database import cursor, database
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

page = 1

def menu(bot, callback):
    markup=InlineKeyboardMarkup(row_width=3)
    item1 = InlineKeyboardButton(text = "Добавить", callback_data = "add")
    item2 = InlineKeyboardButton(text = "Удалить", callback_data = "del")
    item3 = InlineKeyboardButton(text = "Обновить", callback_data = "update")
    item5 = InlineKeyboardButton(text = "Сообщения", callback_data = "mes")
    item6 = InlineKeyboardButton(text = "Мои сообщения", callback_data = "my_mes")
    markup.add(item1, item2, item3)
    markup.add(item6, item5)
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

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши сообщение: ',  parse_mode='html', reply_markup=keyboard)
            
        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            us_id = message.from_user.id
            us_nm = message.from_user.first_name
            cursor.execute('INSERT INTO messages (user_id, user_name, message, like) VALUES (?, ?, ?, ?)', (us_id, us_nm, a[0], 0))
            database.commit()
            bot.send_message(callback.message.chat.id, text = f'Я добавил твоё сообщение: \n{a}', parse_mode='markdown')
            menu(bot, callback.message)
        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'del':
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        cursor.execute(f"""DELETE FROM messages WHERE user_id = {callback.message.chat.id}""")
        database.commit()
        menu(bot, callback.message)

    elif callback.data == 'update':
        markup=InlineKeyboardMarkup(row_width=4)
        item1 = InlineKeyboardButton(text = "Обновить совё сообщение", callback_data = "message")
        back = InlineKeyboardButton(text = "Выйти", callback_data = "close")
        markup.add(item1)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)

    elif callback.data == 'my_mes':
        cursor.execute(f'''SELECT * FROM messages WHERE user_id = {callback.message.chat.id}''')
        health = cursor.fetchall()
        if len(health) == 0:
            bot.send_message(callback.message.chat.id, 'У тебя нету сообщений',  parse_mode='html')
        else:
            for i in health:
                bot.send_message(callback.message.chat.id, text = 
                (
                f'Твоё сообщение: {(i[3])}\n'
                f'У тебя: {i[4]} лайков\n'
                ))
                bot.answer_callback_query(callback_query_id=callback.id, show_alert=False)

    elif callback.data == 'message':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши своё сообщение: ', reply_markup=keyboard)
        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            weight = a[0]
            id = callback.message.chat.id
            cursor.execute(f"""UPDATE messages SET message = ? WHERE user_id = ?""", (weight, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я изменил твоё сообщение на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'close':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        menu(bot, callback.message)

    elif callback.data == 'mes':
        cursor.execute(f'''SELECT * FROM messages''')
        health = cursor.fetchall()
        for i in health:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Лайк', callback_data = f'like_{i[2]}'))
            bot.send_message(callback.message.chat.id, text = 
            (
            f'Написал: {(i[2])}\n'
            f'Сообщение: {(i[3])}\n'
            f'Лайков: {i[4]}\n'
            ), reply_markup=keyboard)
            bot.answer_callback_query(callback_query_id=callback.id, show_alert=False)

    elif callback.data[0:4] == 'like':
        user = callback.data[5:len(callback.data)]
        cursor.execute(f"SELECT like FROM messages WHERE user_name = '{user}'")
        like = cursor.fetchall()
        for i in like:
            new_like = i[0] + 1
        cursor.execute(f"""UPDATE messages SET like = ? WHERE user_name = ?""", (new_like, user))
        database.commit()
        bot.send_message(callback.message.chat.id, text = f'Лайк поставлен', parse_mode='markdown')

