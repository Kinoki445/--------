from database import cursor, database
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import time
from database import cursor

def menu(bot, callback):
    markup=InlineKeyboardMarkup(row_width=3)
    item1 = InlineKeyboardButton(text = "Добавить", callback_data = "add")
    item2 = InlineKeyboardButton(text = "Удалить", callback_data = "del")
    item3 = InlineKeyboardButton(text = "Обновить", callback_data = "update")
    item5 = InlineKeyboardButton(text = "Задачи", callback_data = "tasks")
    markup.add(item1, item5, item3)
    markup.add(item2)
    try:
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)
    except:
        bot.send_message(callback.chat.id, 'Вот что я могу сделать: '.format(callback.from_user),  parse_mode='html', reply_markup=markup)

# Функция, которая будет отправлять сообщение с задачей в указанное время
def send_task(task, bot, message):
    cursor.execute("SELECT user_id FROM tasks")
    user = cursor.fetchall()
    for i in user:
        user = i[0]
    database.commit()
    task_name = task[0]
    task_time = datetime.datetime.strptime(task[1], '%Y-%m-%d %H:%M')
    print(datetime.datetime.now())
    while datetime.datetime.now() < task_time:
        time.sleep(5)  # проверяем каждую минуту, не настало ли время выполнения задачи
    
    bot.send_message(chat_id=user, text=f'Выполните задачу: {task_name}')
    cursor.execute(f"DELETE FROM tasks WHERE user_id = ? AND task = ?", (message.from_user.id, str(task_name)))
    database.commit()

# Функция для запуска всех задач
def start_tasks(bot, message):
    tasks = {}
    cursor.execute("""SELECT * from tasks""")
    user = cursor.fetchall()
    for i in user:
        tasks[i[2]] =  i[3]
    for tasks in tasks.items():
        send_task(tasks, bot, message)

def mycallback(bot, callback):
    if callback.data == 'add':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))

        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши задачу которую хочешь сделать: ',  parse_mode='html', reply_markup=keyboard)

        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши срок выполнения (2023-04-13 13:20)', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, add2)
            
        def add2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            us_id = message.from_user.id
            cursor.execute('INSERT INTO tasks (user_id, task, time) VALUES (?, ?, ?)', (us_id, a[0], a[1]))
            database.commit()
            bot.send_message(callback.message.chat.id, text = f'Я добавил твою задачу в базу данных: \n{a}', parse_mode='markdown')
            menu(bot, callback.message)
        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'del':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши id задачи которую хочешь удалить: ',  parse_mode='html', reply_markup=keyboard)

        def add(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            cursor.execute(f"""DELETE FROM tasks WHERE id = {a[0]}""")
            database.commit()
            menu(bot, callback.message)
        bot.register_next_step_handler(callback.message, add)

    elif callback.data == 'update':
        markup=InlineKeyboardMarkup(row_width=4)
        item1 = InlineKeyboardButton(text = "Задачу", callback_data = "task")
        item2 = InlineKeyboardButton(text = "Время выполнение задачи", callback_data = "time")
        back = InlineKeyboardButton(text = "Выйти", callback_data = "close")
        markup.add(item1, item2)
        markup.add(back)
        try:
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)
        except:
            bot.send_message(callback.chat.id, 'Выбери что ты хотел бы изменить: ',  parse_mode='html', reply_markup=markup)

    elif callback.data == 'tasks':
        cursor.execute(f'''SELECT * FROM tasks WHERE user_id = {callback.message.chat.id}''')
        tasks = cursor.fetchall()
        for i in tasks:
            bot.send_message(callback.message.chat.id, text = 
            (
            f'Id задачи: {(i[0])}\n'
            f'Задача: {(i[2])}\n'
            f'Время выполнения: {(i[3])}\n'
            ))
            bot.answer_callback_query(callback_query_id=callback.id, show_alert=False)

    elif callback.data == 'task':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши задачу котору хотел бы изменить: ', reply_markup=keyboard)
        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши задачу: ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)

        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            task = a[0]
            id = a[1]
            cursor.execute(f"""UPDATE tasks SET weight = ? WHERE id = ?""", (task, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я изменил твою задачу на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'task':
        a = []
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Отмена', callback_data = 'close'))
        bot.send_message(callback.message.chat.id, 'Напиши id задачи которой хотел бы изменить время: ', reply_markup=keyboard)
        def update(message):
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text = 'Напиши время (2023-04-13 13:20): ', reply_markup=keyboard)
            a.append(message.text)
            bot.register_next_step_handler(callback.message, update2)

        def update2(message):
            bot.delete_message(message.chat.id, message.message_id)
            a.append(message.text)
            time = a[0]
            id = a[1]
            cursor.execute(f"""UPDATE tasks SET weight = ? WHERE id = ?""", (time, id))
            database.commit()
            menu(bot, callback.message)
            bot.send_message(callback.message.chat.id, text = f'Я твою задачу на: {a[0]}', parse_mode='markdown')

        bot.register_next_step_handler(callback.message, update)

    elif callback.data == 'close':
            bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
            menu(bot, callback.message)

