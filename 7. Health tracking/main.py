import telebot, time as tm
from telebot import telebot
from database import cursor, db_table_val
from buttons import menu, mycallback
from key import API

bot = telebot.TeleBot(API)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, f'Добро пожаловать {message.from_user.first_name}', parse_mode='html')
    db_table_val(message, bot)

@bot.message_handler(commands=['menu'])
def start_message(message):
    menu(bot, message)

@bot.callback_query_handler(func=lambda callback: callback.data)
def callback(callback):
    mycallback(bot, callback)

@bot.message_handler(content_types=["text"])
def bot_message(message):
    cursor.execute(f'SELECT id FROM users WHERE user_id = {message.chat.id} ')
    data = cursor.fetchone()
    message_to_bot = message.text.lower()

    if message.chat.id != 5322880119:
        if data is None:
            bot.send_message(message.from_user.id, 'Привет, тебя нету в базе данных, не мог бы ты написать /start ?', parse_mode='html')
        else:
            if message.content_type.lower() == 'text':
                if message_to_bot == 'меню' or message_to_bot == 'menu':
                    menu(bot, message)
                    bot.delete_message(message.chat.id, message.message_id)
                    pass

                else:
                    delete = telebot.types.ReplyKeyboardRemove()
                    bot.send_message(message.chat.id, f'Вы написали: {message.text}\nЕсли хотите узнать что может бот напишите /menu\nБудут вопросы пишите: @Kinoki445', parse_mode='html', reply_markup=delete)
                    print(f'Пользователь {message.from_user.username} {message.from_user.first_name} написал {message.text}')
                    bot.delete_message(message.chat.id, message.message_id)

if __name__ == '__main__':
    print ('Бот запущен!')
    while True:
        try:
            bot.infinity_polling(none_stop=True, timeout=123)
        except Exception as e:
            tm.sleep(15)