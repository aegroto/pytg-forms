from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

def append_jump_button(menu_layout, text, step_id):
    menu_layout.append([InlineKeyboardButton(text, callback_data="forms,jump,{}".format(step_id))])

