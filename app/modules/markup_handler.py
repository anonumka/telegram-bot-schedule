from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def faqButton():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Read our FAQ\'s', callback_data='faqCallbackdata'))
    return markup
