import telebot
import gspread
import schedule
import time
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
waiting_for_reading = None
 
# настройки бота
bot_token = '5734635130:AAHFP9kXV43eU8pEq4Wy1c79lYBRqRew60M'
bot = telebot.TeleBot(bot_token)

# настройки Google таблицы
google_sheet_key = '1kH68LGSrnVECyfQBfFhu9B6Nu_s-uZ-G2ogqfK4BkRU'
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/anastasiasolosina/Desktop/telebot/telebot-385720-53e038c6ef30.json',
                                                               ['https://spreadsheets.google.com/feeds',
                                                                'https://www.googleapis.com/auth/drive'])
google_sheet_client = gspread.authorize(credentials)
google_sheet = google_sheet_client.open_by_key(google_sheet_key).sheet1

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    # Отправляем приветственное сообщение
    bot.send_message(message.chat.id, "Привет, я бот, который поможет тебе записывать показания твоих счетчиков, чтобы ты мог вести учет расхода электроэнергии и воды и понимать где ты можешь сэкономить!")

    # Создаем кнопки
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = telebot.types.KeyboardButton('Передать сейчас')
    itembtn2 = telebot.types.KeyboardButton('Напомнить позже')
    markup.add(itembtn1, itembtn2)
    
    # Отправляем сообщение с кнопками
    bot.send_message(message.chat.id, "Вы готовы передать показания сейчас, или вы хотите дождаться удобного для этого времени? Напомню, что наиболее удобным временем для передачи и оплаты показаний счетчиков является каждое 20-е число месяца.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Передать сейчас')
def send_values_handler(message):
    # Отправляем сообщение для ввода показаний
    chat_id = message.chat.id
    bot.send_message(message.chat.id, "Отлично, давайте приступим!")
    time.sleep(1)
    bot.send_message(chat_id, "Начнем с показаний счетчиков электричества, для этого нужно будет выйти в коридор, поэтому накиньте что-нибудь на себя, чтобы не простудиться и обуйтесь")

    # Wait for the first meter reading
    current_question = "Передайте показания Т1"
    bot.send_message(chat_id, current_question)
    waiting_for_reading = "Т1"

@bot.message_handler(func=lambda message: message.text.isdigit() and waiting_for_reading)
def handle_reading(message):
    chat_id = message.chat.id
    global waiting_for_reading
    global current_question

    if waiting_for_reading == "Т1":
        google_sheet.update_cell(row, 5, message.text)
        current_question = "Теперь напишите показания у Т2"
        waiting_for_reading = "Т2"
    elif waiting_for_reading == "Т2":
        google_sheet.update_cell(row, 6, message.text)
        current_question = "Остался только Т3"
        waiting_for_reading = "Т3"
    elif waiting_for_reading == "Т3":
        google_sheet.update_cell(row, 7, message.text)
        current_question = "Отлично! Я записал показания счетчиков электричества, теперь перейдем к счетчикам за воду!"
        bot.send_message(chat_id, current_question)
        current_question = "Возвращайтесь в квартиру и идите в прачечную. Только не забудьте переодеться!"
        waiting_for_reading = "Водомер 1"
    elif waiting_for_reading.startswith("Водомер"):
        if waiting_for_reading == "Водомер 1":
            google_sheet.update_cell(row, 10, message.text)
            current_question = "🔵 Запишите показания Счётчика № 170292059"
            waiting_for_reading = "Водомер 2"
        elif waiting_for_reading == "Водомер 2":
            google_sheet.update_cell(row, 12, message.text)
            current_question = "Осталось чуть-чуть! Теперь идите в туалет"
            waiting_for_reading = "Водомер 3"
        elif waiting_for_reading == "Водомер 3":
            google_sheet.update_cell(row, 14, message.text)
            current_question = "Отлично вы передали показания счетчиков! Теперь вам остается их только оплатить"
            bot.send_message(chat_id, current_question)
            bot.remove_message_handler(handle_reading)
        # Отправляем напоминание на 20-е число месяца
            today = datetime.date.today()
            reminder_date = datetime.date(today.year, today.month, 20)
            if today > reminder_date:
                reminder_date = datetime.date(today.year, today.month+1, 20)
                days_until_reminder = (reminder_date - today).days
                reminder_text = f"Я напомню вам {reminder_date.day} передать показания счетчиков вновь, до встречи!"
                bot.send_message(chat_id, reminder_text)
    else:
        current_question = "Пожалуйста, вводите только цифры"

@bot.message_handler(func=lambda message: message.text == "Напомнить позже")
def remind_later(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Ок, я напомню вам 20 числа передать показания счетчиков")
    
def send_reminder():
    # Отправляем сообщение с напоминанием каждого 20 числа месяца
    today = datetime.today().day
    if today == 20:
        # Создаем кнопки
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = telebot.types.KeyboardButton('Передать сейчас')
        itembtn2 = telebot.types.KeyboardButton('Напомнить позже')
        markup.add(itembtn1, itembtn2)

            # Отправляем сообщение с кнопками
        bot.send_message(message.chat.id, "Вы готовы передать показания сейчас, или вы хотите дождаться удобного для этого времени? Напомню, что наиболее удобным временем для передачи и оплаты показаний счетчиков является каждое 20-е число месяца.", reply_markup=markup)


# функция запуска бота
def run_bot():
    bot.polling(none_stop=True, interval=0)    
    if __name__ == '__main__':

# Регистрируем задачу на выполнение каждый день в полночь
        schedule.every().day.at("09:50").do(send_reminder)

# Запускаем бесконечный цикл, который проверяет расписание и выполняет задачи
    while True:
        schedule.run_pending()
        time.sleep(10000)   
