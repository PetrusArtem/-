import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# настройки бота
bot_token = '5990588377:AAGLUbfFDUQ7GrF6qmTxxZab1oM7TWbgFDM'
bot = telebot.TeleBot(bot_token)

# настройки Google таблицы
google_sheet_key = '1uVzPBQhopvMi9Uj5fvbyQ4nbQsLcWO0QzPp9ch61Dnk'
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/anastasiasolosina/Desktop/telebot/telebot-385720-53e038c6ef30.json',
                                                               ['https://spreadsheets.google.com/feeds',
                                                                'https://www.googleapis.com/auth/drive'])
google_sheet_client = gspread.authorize(credentials)
google_sheet = google_sheet_client.open_by_key(google_sheet_key).sheet1
