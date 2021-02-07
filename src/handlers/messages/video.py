import telegram, logging

from pytg.load import manager

def video_message_handler(update, context):
    bot = context.bot

    message = update.message

    if not message or not message.chat or not message.video:
        return

    chat_id = message.chat.id
    message_id = message.message_id

    username = message.from_user.username
    user_id = message.from_user.id

    logging.info("Received video message update from {} ({}) in chat {}".format(username, user_id, chat_id))

    data_manager = manager("data")

    # Check if the bot is waiting for a form input 
    if data_manager.has_data("forms", "forms", chat_id):
        current_user_form_id = chat_id
        forms_manager = manager("forms")

        form_data = data_manager.load_data("forms", "forms", current_user_form_id)

        if form_data["digested"]:
            return

        module_name = form_data["module_name"]
        form_name = form_data["form_name"]
        form_steps = forms_manager.load_form_steps(module_name, form_name)

        step_data = form_steps[form_data["current_step"]]

        if step_data["type"] != "video_field":
            return

        video = message.video
        video_id = video.file_id
        video_url = bot.getFile(video_id).file_path

        input_data = {
            "video_id": video_id,
            "video_url": video_url 
        }

        forms_manager = manager("forms")
        forms_manager.handle_input(context, chat_id, message_id, module_name, form_name, form_data["current_step"], input_data)

