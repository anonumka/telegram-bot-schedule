from telebot import TeleBot
from app.modules.json_parser import settings
from app.modules.database import Database

token = settings['bot_token']

bot = TeleBot(token)

database = Database()
