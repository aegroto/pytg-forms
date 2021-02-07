from pytg.load import manager, get_module_id

from .FormsManager import FormsManager

from telegram.ext import CallbackQueryHandler, MessageHandler, Filters 

from modules.forms.handlers.callback.forms import forms_callback_handler

from modules.forms.handlers.messages.text import text_message_handler
from modules.forms.handlers.messages.photo import photo_message_handler
from modules.forms.handlers.messages.video import video_message_handler
from modules.forms.handlers.messages.animation import animation_message_handler

def load_messages_handlers(dispatcher):
    module_id = get_module_id("forms")

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.video, video_message_handler), group=module_id)
    dispatcher.add_handler(MessageHandler(Filters.animation, animation_message_handler), group=module_id)

def load_callback_handlers(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(forms_callback_handler, pattern="forms,.*"))

def connect():
    bot_manager = manager("bot")

    load_callback_handlers(bot_manager.updater.dispatcher)
    load_messages_handlers(bot_manager.updater.dispatcher)

def initialize_manager():
    return FormsManager()

def depends_on():
    return ["bot", "data", "text"]