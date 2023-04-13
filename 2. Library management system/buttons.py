from database import cursor, database
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

page = 1

def menu(bot, callback):
    markup=InlineKeyboardMarkup(row_width=3)
    item1 = InlineKeyboardButton(text = "Добавить", callback_data = "add")
    item2 = InlineKeyboardButton(text = "Удалить", callback_data = "del")
    item3 = InlineKeyboardButton(text = "Обновить", callback_data = "update")
    item5 = InlineKeyboardButton(text = "Книги", callback_data = "book")
    markup.add(item1, item2, item3, item5)
    try:
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)
    except:
        bot.send_message(callback.chat.id, 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)

def defuser(bot, message, InlineKeyboardMarkup, InlineKeyboardButton):
    cursor.execute('''SELECT * FROM book''')
    global book
    book = cursor.fetchall()
    global page
    markup = InlineKeyboardMarkup()
    back = InlineKeyboardButton(text = '🔙Назад', callback_data = 'close')
    markup.row_width = 1
    max = page * 10
    min = max - 10
    a = 0
    b = 0

    if page == 0:
        page = page + 1

    for i in book[min:max:]:
        id = str(i[0])
        markup.add (InlineKeyboardButton(text = f'{i[2]} | {i[3]}', callback_data = id))
        a = a + 1
        b = b + a

    if page == 1:
        amount_plus = InlineKeyboardButton(text = 'Вперёд -->', callback_data = '+1')
        maxpage = InlineKeyboardButton(text = 'Конец', callback_data='maxpage')
        markup.add (maxpage, amount_plus, row_width = 4)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)
        except:
            bot.send_message (message.chat.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)

    elif a < 10:
        amount_minus = InlineKeyboardButton(text = '<-- Назад', callback_data = '-1')
        start = InlineKeyboardButton(text = 'Начало', callback_data='minpage')
        maxpage = InlineKeyboardButton(text = 'Конец', callback_data='maxpage')
        markup.add(amount_minus, start,maxpage, row_width = 4)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)
        except:
            bot.send_message(message.chat.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)
    else:
        amount_minus = InlineKeyboardButton(text = '<-- Назад', callback_data = '-1')
        amount_plus = InlineKeyboardButton(text = 'Вперёд -->', callback_data = '+1')
        start = InlineKeyboardButton(text = 'Начало', callback_data='minpage')
        maxpage = InlineKeyboardButton(text = 'Конец', callback_data='maxpage')
        markup.add (amount_minus, start, maxpage, amount_plus, row_width = 4)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)
        except:
            bot.send_message(message.chat.id, text = f'**Список {page}**', parse_mode='markdown', reply_markup = markup)

# callback
def mycallback(bot, callback):
    if callback.data == 'add':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши название книги: ',  parse_mode='html', reply_markup=keyboard)

        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши автора книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add2)
            
        def add2(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши количество экземляров книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add3)
        
        def add3(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши ISBN книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add4)
            
        def add4(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            us_id = message.from_user.first_name
            cursor.execute('INSERT INTO book (user_id, author, title, Nof, ISBN) VALUES (?, ?, ?, ?, ?)', (us_id, a[1], a[0], a[2], a[3]))
            database.commit()
            bot.send_message(callback.message.chat.id, text = f'Я добавил твою книгу в базу данных: \n{a}', parse_mode='markdown')
            menu(bot, callback)
        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'del':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id книги которую хочешь удалить: ', reply_markup=keyboard)

        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            cursor.execute(f"""DELETE FROM book where id = {a[0]}""")
            database.commit()
            menu(bot, callback)

        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'update':
        markup=InlineKeyboardMarkup(row_width=4)
        item1 = InlineKeyboardButton(text = "Автор", callback_data = "author")
        item2 = InlineKeyboardButton(text = "Название книги", callback_data = "title")
        item3 = InlineKeyboardButton(text = "Количество экземпляров", callback_data = "nof")
        item5 = InlineKeyboardButton(text = "ISBN", callback_data = "isbn")
        back = InlineKeyboardButton(text = "Выйти", callback_data = "close")
        markup.add(item1, item2, item3, item5)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)

    elif callback.data == 'book':
        defuser(bot, callback.message, InlineKeyboardMarkup, InlineKeyboardButton)

    elif callback.data == 'close':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        menu(bot, callback.message)

    elif callback.data == 'author':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id книги которую хочешь изменить: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши автора книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)
            
        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            author = str(a[1])
            id = a[0]
            cursor.execute(f"""UPDATE book SET author = ? WHERE id = ?""", (author, id))
            database.commit()
            menu(bot, callback)
            bot.send_message(callback.message.chat.id, text = f'Я изменил автора книги на: {a[1]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'title':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id книги которую хочешь изменить: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши название книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)
            
        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            title = str(a[1])
            id = a[0]
            cursor.execute(f"""UPDATE book SET title = ? WHERE id = ?""", (title, id))
            database.commit()
            menu(bot, callback)
            bot.send_message(callback.message.chat.id, text = f'Я изменил название книги на: {a[1]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'nof':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id книги которую хочешь изменить: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши количество экземпляров книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)
            
        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            nof = a[1]
            id = a[0]
            cursor.execute(f"""UPDATE book SET Nof = ? WHERE id = ?""", (nof, id))
            database.commit()
            menu(bot, callback)
            bot.send_message(callback.message.chat.id, text = f'Я изменил название количество экземпляров на: {a[1]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'isbn':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id книги которую хочешь изменить: ', reply_markup=keyboard)

        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши ISBN книги: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)
            
        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            nof = str(a[1])
            id = a[0]
            cursor.execute(f"""UPDATE book SET ISBN = ? WHERE id = ?""", (nof, id))
            database.commit()
            menu(bot, callback)
            bot.send_message(callback.message.chat.id, text = f'Я изменил название ISBN на: {a[1]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == '+1':
        global page 
        page += 1
        defuser(bot, callback.message, InlineKeyboardMarkup, InlineKeyboardButton)

    elif callback.data == '-1':
        page -= 1
        defuser(bot, callback.message, InlineKeyboardMarkup, InlineKeyboardButton)

    elif callback.data == 'maxpage':
        cursor.execute('''SELECT * FROM users''')
        user = cursor.fetchall()
        page = len(user) // 10
        defuser(bot, callback.message, InlineKeyboardMarkup, InlineKeyboardButton)
    
    elif callback.data == 'minpage':
        page = 1
        defuser(bot, callback.message, InlineKeyboardMarkup, InlineKeyboardButton)

    cursor.execute('''SELECT * FROM book''')
    book = cursor.fetchall()
    for i in book:
        if callback.data == str(i[0]):
            bot.send_message(callback.message.chat.id, text = 
            (
            f'id: {str(i[0])}\n'
            f'Кто добавил Книгу: {str(i[1])}\n'
            f'Автор: {str(i[2])}\n'
            f'Название: {str(i[3])}\n'
            f'Количество: {str(i[4])}\n'
            f'ISBN: {str(i[5])}\n'
            ))
            bot.answer_callback_query(callback_query_id=callback.id, show_alert=False)