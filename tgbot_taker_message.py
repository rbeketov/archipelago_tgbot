import os
import logging
import requests
import json
import telebot

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL_SUMMARAIZE = os.environ.get("URL_SUMMARAIZE")
TOKEN = os.environ.get("TOKEN")

LOGS_DIR = "logs/"

logger = logging.getLogger(__name__)
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
handler = logging.FileHandler(f"{LOGS_DIR}/server.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['config'])
def config(message):
    print(message.text[len("/config"):].strip())


@bot.message_handler(commands=['get-summ'])
def summaraize(message):
    with open('data/test.txt', 'r') as file:
        chat_content = file.read()

    url = URL_SUMMARAIZE
    payload = {
        "token": TOKEN,
        "text": chat_content,
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        response_json = response.json()
        summ_text = response_json["summ_text"]
        bot.reply_to(message, summ_text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Что-то полшло не так, попробуйте ещё раз")


@bot.message_handler(func=lambda m: True)
def repeat_all_messages(message):
    try:
        reply_user_name = f"{message.reply_to_message.from_user.first_name} {message.reply_to_message.from_user.last_name}"
    except Exception as e:
        reply_user_name = None
    #print(reply_user_name)
    #print(message.date)
    user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    user_message = message.text

    # TODO поход в Click
    with open('data/test.txt', 'a') as file:
        if reply_user_name:
            file.write(f"{user_name}: {user_message} - в ответ пользователю {reply_user_name}\n")
        else:    
            file.write(f"{user_name}: {user_message}\n")


if __name__ == "__main__":
    bot.polling()
