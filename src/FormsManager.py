import telegram, yaml, logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from pytg.Manager import Manager
from pytg.load import manager, get_module_content_folder 

from .utils.reply_markup_builders import *
from .utils.various import *

class FormsManager(Manager):
    def __init__(self):
        self.digesters = { }

    ###################
    # Forms interface #
    ###################

    def add_digester(self, key, func):
        self.digesters[key] = func

    def clear_user_form_data(self, context, chat_id, delete_messages=True):
        logging.info("Clearing form data for user {}".format(chat_id))

        data_manager = manager("data")

        form_id = chat_id
        if not data_manager.has_data("forms", "forms", form_id):
            return

        form_data = data_manager.load_data("forms", "forms", form_id)

        # Clear form messages
        if delete_messages: # (not form_data["digested"]) and delete_messages:
            for form_message_id in form_data["messages"]:
                try:
                    context.bot.deleteMessage(
                        chat_id = chat_id,
                        message_id = form_message_id
                    )
                except:
                    logging.info("Unable to delete message {}".format(form_message_id))

        # Update form data
        data_manager.delete_data("forms", "forms", form_id)

    def start_form(self, context, chat_id, module_name, form_name, form_meta={}, lang=None):
        logging.info("Starting form {} for {}".format(form_name, chat_id))

        data_manager = manager("data")

        # Create user's form data
        self.clear_user_form_data(context, chat_id)

        form_id = chat_id
        data_manager.create_data("forms", "forms", form_id)

        steps = self.load_form_steps(module_name, form_name)

        first_step = steps["info"]["first_step"]

        form_data = data_manager.load_data("forms", "forms", form_id)

        form_data["module_name"] = module_name
        form_data["form_name"] = form_name
        form_data["current_step"] = first_step
        form_data["form_meta"] = form_meta
        
        if not lang:
            config_manager = manager("config")
            lang_settings = config_manager.load_settings("forms", "lang")
            lang = lang_settings["default"]

        form_data["lang"] = lang

        # Set default entries
        if "default_entries" in steps["info"].keys():
            default_entries = steps["info"]["default_entries"]

            for entry in default_entries.keys():
                form_data["form_entries"][entry] = default_entries[entry]

        data_manager.save_data("forms","forms", form_id, form_data)

        self.show_current_step(context, chat_id, lang)

    def set_next_step(self, context, chat_id, message_id, next_step=None):
        bot = context.bot

        data_manager = manager("data")

        form_id = chat_id

        form_data = data_manager.load_data("forms", "forms", form_id)
        module_name = form_data["module_name"]
        form_name = form_data["form_name"]
        form_steps = self.load_form_steps(module_name, form_name)

        current_step_data = form_steps[form_data["current_step"]]

        # Delete previous message if 'clear' is true
        if "clear" in current_step_data and current_step_data["clear"]:
            context.bot.deleteMessage(
                chat_id = chat_id,
                message_id = message_id
            )

        if next_step == None:
            next_step = current_step_data["next_step"]

        logging.info("Showing next step to {} ({} {})".format(chat_id, form_id, next_step))

        if next_step and next_step != "None":
            if next_step == "_RESET":
                self.clear_user_form_data(context, chat_id, False)
                return 

            form_data["current_step"] = next_step
            data_manager.save_data("forms","forms", form_id, form_data)
            self.show_current_step(context, chat_id, form_data["lang"])
        else:
            if "void" in form_steps["info"] and form_steps["info"]["void"]:
                return

            self.digest_form(context, chat_id, form_id)

    def digest_form(self, context, chat_id, form_id):
        logging.info("Digesting form for {}".format(chat_id))

        data_manager = manager("data")

        # Load form's data 
        form_data = data_manager.load_data("forms", "forms", form_id)
        form_name = form_data["form_name"]

        # Update digestion flag
        form_data["digested"] = True
        data_manager.save_data("forms","forms", form_id, form_data)

        # Digest the form
        digester = self.digesters[form_name]
        digester(context, chat_id, form_data["form_entries"], form_data["form_meta"])

    def format_step_text(self, step_text, form_entries):
        for key in form_entries.keys():
            key_expression = "[{}]".format(key)
            step_text = step_text.replace(key_expression, str(form_entries[key]).replace("_", "\\_"))

        return step_text

    def show_current_step(self, context, chat_id, lang, message_id=None):
        data_manager = manager("data")

        form_id = chat_id

        form_data = data_manager.load_data("forms", "forms", form_id)
        module_name = form_data["module_name"]
        form_name = form_data["form_name"]
        form_steps = self.load_form_steps(module_name, form_name)

        step_name = form_data["current_step"]
        current_step_data = form_steps[step_name]

        if "externs" in current_step_data.keys():
            externs = current_step_data["externs"]

            for extern_key in externs.keys():
                extern_data = form_data["form_meta"][externs[extern_key]]

                current_step_data[extern_key] = extern_data

        next_step = "__NULL"

        phrases = self.load_form_phrases(module_name, form_name, lang)

        step_text = phrases[current_step_data["phrase"]]

        if "reply_markup" in current_step_data.keys():
            reply_markup_data = current_step_data["reply_markup"]

            menu_module = module_name if "module" not in reply_markup_data else reply_markup_data["module"]
            menu_id = reply_markup_data["id"]

            reply_markup = manager("menu").create_reply_markup(menu_module, menu_id, meta=form_data["form_meta"])
        else:
            reply_markup = None

        if "format" in current_step_data.keys() and current_step_data["format"]:
            form_entries = form_data["form_entries"]
            step_text = self.format_step_text(step_text, form_entries)

        # Replace macros in meta
        for meta in form_data["form_meta"].keys():
            macro = "[{}]".format(meta)

            step_text = step_text.replace(macro, str(form_data["form_meta"][meta]))

        # Message 
        if current_step_data["type"] == "message":
            next_step = current_step_data["next_step"]

        # Text or image field
        if (current_step_data["type"] == "text_field" or
            current_step_data["type"] == "image_field" or
            current_step_data["type"] == "video_field" or
            current_step_data["type"] == "animation_field"):
            pass

        # Fixed reply
        if current_step_data["type"] == "fixed_reply":
            options = current_step_data["options"]
            reply_markup = fixed_reply_reply_markup(options, form_data, current_step_data)

        # Keyboard reply
        if current_step_data["type"] == "keyboard_reply":
            options = current_step_data["options"]
            reply_markup = keyboard_reply_reply_markup(options, form_data, current_step_data)

        # Checkbox list 
        if current_step_data["type"] == "checkbox_list":
            step_output = current_step_data["output"]

            if step_output not in form_data["form_entries"].keys():
                form_data["form_entries"][step_output] = []
                data_manager.save_data("forms","forms", form_id, form_data)

            entries = current_step_data["entries"]
            reply_markup = checkbox_list_reply_markup(entries, form_data, current_step_data)

        # Disable web page preview option
        disable_web_page_preview = True
        if "disable_web_page_preview" in current_step_data.keys() and current_step_data["disable_web_page_preview"]:
            disable_web_page_preview = current_step_data["disable_web_page_preview"]

        # Send or edit message
        if message_id:
            context.bot.editMessageText(
                chat_id=chat_id,
                message_id=message_id,
                text=step_text,
                parse_mode=telegram.ParseMode.MARKDOWN,
                reply_markup = reply_markup,
                disable_web_page_preview = disable_web_page_preview
            )
        else:
            # Load media data (if any)
            media_data = None
            if "media" in current_step_data.keys() and current_step_data["media"]:
                media_data = current_step_data["media"]

                for meta in form_data["form_meta"].keys():
                    macro = "[{}]".format(meta)

                    media_data["type"] = media_data["type"].replace(macro, str(form_data["form_meta"][meta]))
                    media_data["path"] = media_data["path"].replace(macro, str(form_data["form_meta"][meta]))

                if "format" in current_step_data.keys() and current_step_data["format"]:
                    for key in form_data["form_entries"].keys():
                        macro = "[{}]".format(key)

                        media_data["type"] = media_data["type"].replace(macro, str(form_data["form_entries"][key]))
                        media_data["path"] = media_data["path"].replace(macro, str(form_data["form_entries"][key]))

            # Send complete message
            if not media_data:
                sent_message = context.bot.sendMessage(
                    chat_id=chat_id,
                    text=step_text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup = reply_markup,
                    disable_web_page_preview = disable_web_page_preview
                )
            else:
                if media_data["type"] == "photo":
                    sent_message = context.bot.sendPhoto(
                        chat_id=chat_id,
                        caption=step_text,
                        photo=media_data["path"],
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup = reply_markup,
                        disable_web_page_preview = disable_web_page_preview
                    )
                elif media_data["type"] == "video":
                    sent_message = context.bot.sendVideo(
                        chat_id=chat_id,
                        caption=step_text,
                        video=media_data["path"],
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup = reply_markup,
                        disable_web_page_preview = disable_web_page_preview
                    )
                else:
                    logging.exception("Unknown media type")

            # Add new message IDs
            if data_manager.has_data("forms", "forms", form_id):
                form_data = data_manager.load_data("forms", "forms", form_id)
                form_data["messages"].append(sent_message.message_id)
                data_manager.save_data("forms","forms", form_id, form_data)

        if next_step is not "__NULL":
            self.set_next_step(context, chat_id, sent_message.message_id, next_step = next_step)

    def handle_input(self, context, chat_id, message_id, module_name, form_name, step_name, input_data):
        logging.info("Handling input of {} on form {} (step name = {}, input data = {})".format(chat_id, form_name, step_name, input_data))

        data_manager = manager("data")

        next_step_name = None

        # Check if it's an action input
        if "action" in input_data.keys() and len(input_data["action"]) > 0:
            actions = input_data["action"].split(";")

            if actions[0] == "jump":
                next_step_name = actions[1]

        form_steps = self.load_form_steps(module_name, form_name)
        step_data = form_steps[step_name]

        if "output" in step_data.keys():
            if step_data["type"] == "text_field":
                step_output = input_data["text"]

            elif step_data["type"] == "fixed_reply":
                step_output = input_data["output_data"]

            elif step_data["type"] == "keyboard_reply":
                step_output = input_data["value"]

            elif step_data["type"] == "image_field":
                step_output = input_data["image_id"]

            elif step_data["type"] == "video_field":
                step_output = input_data["video_id"]

            elif step_data["type"] == "animation_field":
                step_output = input_data["animation_id"]

            current_user_form_id = chat_id
            form_data = data_manager.load_data("forms", "forms", current_user_form_id)
            form_data["form_entries"][step_data["output"]] = step_output
            data_manager.save_data("forms", "forms", current_user_form_id, form_data)

        self.set_next_step(context, chat_id, message_id, next_step=next_step_name)

    def load_form_steps(self, module_name, form_name):
        module_folder = get_module_content_folder(module_name)

        return yaml.safe_load(open("{}/forms/formats/{}.yaml".format(module_folder, form_name), "r", encoding="utf8"))

    def load_form_phrases(self, module_name, form_name, lang):
        module_folder = get_module_content_folder(module_name)

        return yaml.safe_load(open("{}/forms/phrases/{}/{}.yaml".format(module_folder, lang, form_name), "r", encoding="utf8"))


