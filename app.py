import os
import logging
import requests
import json
from enum import Enum

from db import ClickClient


from flask import Flask, request, jsonify, abort, Blueprint
from flask_cors import CORS

from dotenv import load_dotenv


load_dotenv()

LOGS_DIR = "logs/"
IND_CHAT_ID = 0
IND_ID_MESSAGE = 1
IND_MESSAGE = 3
IND_SPEAKER = 2
IND_REPLY_USER_NAME = 4
IND_TIME_STAMP = 5


URL_SUMMARAIZE = os.environ.get("URL_SUMMARAIZE")
TOKEN = os.environ.get("TOKEN")

logger = logging.getLogger(__name__)
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
handler = logging.FileHandler(f"{LOGS_DIR}/server.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class RequestFields(Enum):
    TOKEN_VALUE = "token"
    NOTE_TOKEN = "token_note"


app = Flask(__name__)
CORS(app)

click = ClickClient()

@app.route('/get-chat-summarize', methods=['POST'])
def get_summarize():
    try:
        logger.info("Got request:", request.json)

        token = request.json[RequestFields.TOKEN_VALUE.value]
        if token != TOKEN:
            logger.warning("Не совпадает токен")
            return abort(403)

        note_token = request.json[RequestFields.NOTE_TOKEN.value]
        logger.info(f"пришёл токен: {note_token}")
        chat_id = click.get_chat_id_for_token(note_token)
        if chat_id is None:
            logger.warning("нет такого чата")
            return abort(404)

        message_rows = click.get_chat_message(chat_id)

        chat_content = ""
        for row in message_rows:
            if row[IND_REPLY_USER_NAME]:
                curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}, в ответ {row[IND_REPLY_USER_NAME]}\n"
            else:
                curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}\n"

            chat_content += curr_mess

        if not chat_content:
            logger.info("Отдаём \'Слишком мало сообщений\'")
            json_data = {"summ_text": "Слишком мало сообщений"}
            return jsonify(json_data)

        url = URL_SUMMARAIZE
        payload = {
            "token": TOKEN,
            "text": chat_content,
            "temperature": 0.9,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        response_json = response.json()
        summ_text = response_json["result"]
        logger.info(f"От GPT пришло {summ_text}")
        logger.debug("Summ_text:", summ_text)
        json_data = {"summ_text": summ_text}
        return jsonify(json_data)
    except Exception as e:
        logger.error("Поймали исключение")
        logger.error(f"Ошибка: {e}")
        return abort(400, e)


@app.route('/exist-notes-link', methods=['POST'])
def check_exist_notes_link():
    try:
        logger.info("Got request:", request.json)
        token = request.json[RequestFields.TOKEN_VALUE.value]
        if token != TOKEN:
            logger.warning("Не совпадает токен")
            return abort(403)

        note_token = request.json[RequestFields.NOTE_TOKEN.value]
        logger.info(f"пришёл токен: {note_token}")
        chat_data = click.get_chat_data_for_token(note_token)
        if chat_data is None:
            logger.warning("нет такого чата")
            return abort(404)

        return jsonify(chat_data)

    except Exception as e:
        logger.error("Поймали исключение")
        logger.error(f"Ошибка: {e}")
        return abort(400, e)


@app.route('/delete-notes-link', methods=['DELETE'])
def check_exist_notes_link():
    try:
        logger.info("Got request:", request.json)
        token = request.json[RequestFields.TOKEN_VALUE.value]
        if token != TOKEN:
            logger.warning("Не совпадает токен")
            return abort(403)

        note_token = request.json[RequestFields.NOTE_TOKEN.value]
        logger.info(f"пришёл токен: {note_token}")
        status = click.delete_token_link(note_token)
        if not status:
            logger.warning(f"замтека {RequestFields.NOTE_TOKEN.value} не приявзана")
            return abort(404, "Эта замтека не приявзана")
        return '', 200
    except Exception as e:
        logger.error("Поймали исключение")
        logger.error(f"Ошибка: {e}")
        return abort(400, e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
