import os
import logging
import requests
import json
import telebot

from dotenv import load_dotenv
from db import ClickClient

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL_SUMMARAIZE = os.environ.get("URL_SUMMARAIZE")
TOKEN = os.environ.get("TOKEN")

IND_CHAT_ID = 0
IND_ID_MESSAGE = 1
IND_MESSAGE = 3
IND_SPEAKER = 2
IND_REPLY_USER_NAME = 4
IND_TIME_STAMP = 5


LOGS_DIR = "logs/"

logger = logging.getLogger(__name__)
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
handler = logging.FileHandler(f"{LOGS_DIR}/bot.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


bot = telebot.TeleBot(BOT_TOKEN)
click = ClickClient()


@bot.message_handler(commands=['config'])
def config(message):
    try:
        try:
            token = message.text[len("/config"):].split()[0].strip()
            if not token:
                bot.reply_to(message, "Токен не найден")
                return
        except Exception as e:
            logger.error(f"Не получилось привести токен к int: {e}")
            bot.reply_to(message, "Токен не найден")
            return

        click.insert_or_update_token(token, message.chat.id)
        bot.reply_to(message, f"Заметка с токеном {token} удачно привязана к этому чату")
    except Exception as e:
        logger.error(f"Не получилось установить токен: {e}")
        bot.reply_to(message, "Что-то пошло не так, попробуй снова")


@bot.message_handler(commands=['get-summ'])
def summaraize(message):
    message_rows = click.get_chat_message(message.chat.id)
    chat_content = ""
    for row in message_rows:
        if row[IND_REPLY_USER_NAME]:
            curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}, в ответ {row[IND_REPLY_USER_NAME]}\n"
        else:
            curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}\n"

        chat_content += curr_mess

    url = URL_SUMMARAIZE
    payload = {
        "token": TOKEN,
        "text": chat_content,
        "temperature": 0.9,
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        response_json = response.json()
        summ_text = response_json["result"]
        bot.reply_to(message, summ_text)
    except Exception as e:
        logger.error(f"Не пришла суммаризация: {e}")
        bot.reply_to(message, "Что-то полшло не так, попробуйте ещё раз")


@bot.message_handler(func=lambda m: True)
def write_messages_to_click(message):
    try:
        reply_user_name = f"{message.reply_to_message.from_user.first_name} {message.reply_to_message.from_user.last_name}"
    except Exception as e:
        reply_user_name = ""
    user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    user_message = message.text

    try:
        click.insert_new_message(
            message.chat.id,
            message.id,
            user_name,
            user_message,
            reply_user_name,
            message.date,
        )
    except Exception as e:
       logger.error(f"Не получилось сохранить в клику сообщение: {e}")


if __name__ == "__main__":
    bot.polling()
