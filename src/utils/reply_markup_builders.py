from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from modules.pytg.ModulesLoader import ModulesLoader

from .various import append_jump_button

def fixed_reply_reply_markup(options, form_data, current_step_data):
    forms_manager = ModulesLoader.load_manager("forms")
    phrases = forms_manager.load_form_phrases(form_data["module_name"], form_data["form_name"], form_data["lang"])

    menu_layout = []

    for options_row in options:
        row = []

        for option in options_row:
            action = ""

            if "action" in option.keys():
                action = option["action"]

            button_data = "forms,fixed_reply,{},{}".format(action, option["output_data"])

            if "text" in option:
                text = option["text"]
            else:
                text = phrases[option["phrase"]]

            row.append(InlineKeyboardButton(text, callback_data=button_data))

        menu_layout.append(row)

    if "previous_step" in current_step_data.keys():
        append_jump_button(menu_layout, "Back", current_step_data["previous_step"])

    reply_markup = InlineKeyboardMarkup(menu_layout)

    return reply_markup

def keyboard_reply_reply_markup(options, form_data, current_step_data):
    menu_layout = []

    for options_row in options:
        row = []

        for option in options_row:
            row.append(KeyboardButton(option["text"]))

        menu_layout.append(row)

    reply_markup = ReplyKeyboardMarkup(menu_layout, resize_keyboard=True, one_time_keyboard=True)

    return reply_markup

def checkbox_list_reply_markup(entries, form_data, current_step_data):
    step_output = current_step_data["output"]

    # Add entries
    menu_layout = []

    for entries_row in entries:
        row = []

        for entry in entries_row:
            text = entry["text"]
            data = str(entry["data"])

            checked = data in form_data["form_entries"][step_output]

            button_data = "forms,checkbox_click,{},{}".format(data, step_output)

            emoji = "✅" if checked else ""

            row.append(InlineKeyboardButton("{} {}".format(text, emoji), callback_data=button_data))

        menu_layout.append(row)

    # Check if the step requires a back button
    if "previous_step" in current_step_data.keys():
        append_jump_button(menu_layout, "Back", current_step_data["previous_step"])

    # Add 'Confirm' button
    append_jump_button(menu_layout, "Confirm", current_step_data["confirm_step"])

    reply_markup = InlineKeyboardMarkup(menu_layout)

    return reply_markup