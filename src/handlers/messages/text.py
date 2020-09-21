import telegram, logging

from modules.pytg.load import manager

logger = logging.getLogger(__name__)

def text_message_handler(update, context):
    bot = context.bot

    message = update.message

    if not message or not message.chat:
        return

    chat_id = message.chat.id
    message_id = message.message_id

    username = message.from_user.username
    user_id = message.from_user.id

    text = message.text

    logger.info("Received text message update from {} ({}) in chat {}: {}".format(username, user_id, chat_id, text))

    # Check if the bot is waiting for a form input 
    if not manager("data").has_data("forms", "forms", chat_id):
        logger.info("No form data available for this user")
        return

    current_user_form_id = chat_id

    form_data = manager("data").load_data("forms", "forms", current_user_form_id)

    if form_data["digested"]:
        logger.info("Form has been digested")
        return

    module_name = form_data["module_name"]
    form_name = form_data["form_name"]
    form_steps = manager("forms").load_form_steps(module_name, form_name)

    step_data = form_steps[form_data["current_step"]]

    if step_data["type"] == "text_field":
        input_data = {
            "text": text
        }

    elif step_data["type"] == "keyboard_reply":
        replies_map = step_data["map"] 

        if text not in replies_map.keys():
            return

        input_data = {
            "value": replies_map[text]
        }
    else:
        return

    manager("forms").handle_input(context, chat_id, message_id, module_name, form_name, form_data["current_step"], input_data)
