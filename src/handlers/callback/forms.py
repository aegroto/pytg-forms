import logging

from pytg.load import manager

def forms_callback_handler(update, context):
    bot = context.bot

    forms_manager = manager("forms")

    query = update.callback_query
    query_data = query.data.split(",")
    user_id = query.from_user.id

    username = query.message.chat.username
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    logging.info("Handling forms callback data from {}: {}".format(chat_id, query_data))

    if query_data[1] == "fixed_reply":
        data_manager = manager("data")

        form_data = data_manager.load_data("forms", "forms", chat_id)

        step_name = form_data["current_step"]

        # step_name = query_data[2]
        # form_name = query_data[3]

        input_data = {
            "action": query_data[2],
            "output_data": query_data[3]
        }

        bot.editMessageReplyMarkup(
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = None
        )

        forms_manager.handle_input(context, chat_id, message_id, form_data["module_name"], form_data["form_name"], step_name, input_data)
        return

    if query_data[1] == "jump":
        next_step_name = query_data[2]

        bot.editMessageReplyMarkup(
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = None
        )

        forms_manager.set_next_step(context, chat_id, message_id, next_step=next_step_name)
        return

    if query_data[1] == "show":
        module_name = query_data[2]
        form_name = query_data[3]

        forms_manager.start_form(context, chat_id, module_name, form_name)

    if query_data[1] == "checkbox_click":
        entry = str(query_data[2])
        step_output = query_data[3]

        form_id = chat_id

        data_manager = manager("data")
        form_data = data_manager.load_data("forms", "forms", form_id)

        if entry in form_data["form_entries"][step_output]:
            form_data["form_entries"][step_output].remove(entry)
        else:
            form_steps = forms_manager.load_form_steps(form_data["module_name"], form_data["form_name"])

            current_step_data = form_steps[form_data["current_step"]]

            if "max_selections" in current_step_data and len(form_data["form_entries"][step_output]) >= current_step_data["max_selections"]:
                return

            form_data["form_entries"][step_output].append(entry)

        data_manager.save_data("forms","forms", form_id, form_data)

        forms_manager.show_current_step(context, chat_id, form_data["lang"], message_id)