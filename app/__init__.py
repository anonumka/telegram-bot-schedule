from telebot import TeleBot
from app.modules.json_parser import settings
from app.modules.database import Database

token = settings['token']

bot = TeleBot(token)

db = Database()


