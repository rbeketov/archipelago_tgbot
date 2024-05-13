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


MAX_LEN_MESSAGE = 15_000

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
    ROLE = "role"
    SUMMARY_DETAIL = "summary_detail"


app = Flask(__name__)
CORS(app)

click = ClickClient()


@app.route('/get-chat-summarize', methods=['POST'])
def get_summarize():
    try:
        logger.info("Endpoint get-chat-summarize")

        token = request.json[RequestFields.TOKEN_VALUE.value]
        if token != TOKEN:
            logger.warning("Not valid")
            return abort(403)

        note_token = request.json[RequestFields.NOTE_TOKEN.value]
        logger.info(f"пришёл токен: {note_token}")
        chat_id = click.get_chat_id_for_token(note_token)
        if chat_id is None:
            logger.warning("нет такого чата")
            return abort(404)

        message_rows = click.get_chat_message(chat_id)

        if not message_rows:
            logger.info("Отдаём \'Слишком мало сообщений\'")
            json_data = {"summ_text": "Слишком мало сообщений"}
            return jsonify(json_data)

        logger.debug(f"last message: {message_rows[-1][IND_MESSAGE]}")
        time_last_message = message_rows[-1][IND_TIME_STAMP]
        last_summ = click.get_last_summarize_by_chat_id(chat_id)

        if last_summ and time_last_message == last_summ[0][1]:
            json_data = {"summ_text": last_summ[0][0]}
            return jsonify(json_data)

        chat_content = ""
        for row in message_rows:
            if row[IND_REPLY_USER_NAME]:
                curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}, в ответ {row[IND_REPLY_USER_NAME]}\n"
            else:
                curr_mess = f"{row[IND_SPEAKER]}: {row[IND_MESSAGE]}\n"

            chat_content += curr_mess

        logger.info(f"endpoint get-chat-summarize: len chat_content = {len(chat_content)}")
        if len(chat_content) > MAX_LEN_MESSAGE:
            chat_content = chat_content[-MAX_LEN_MESSAGE:]

        url = URL_SUMMARAIZE
        payload = {
            "token": TOKEN,
            "text": chat_content,
            "temperature": 0,
            "summary_detail": "Средняя"
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        response_json = response.json()
        summ_text = response_json["result"]
        logger.info(f"От GPT пришло {summ_text}")

        click.insert_new_summarization(
            chat_id=chat_id,
            note_id=note_token,
            summary=summ_text,
            timestamp_last_message=time_last_message,
        )

        json_data = {"summ_text": summ_text}
        return jsonify(json_data)
    except Exception as e:
        logger.error("Поймали исключение")
        logger.error(f"Ошибка: {e}")
        return abort(400, e)


@app.route('/exist-notes-link', methods=['POST'])
def check_exist_notes_link():
    try:
        logger.info("endpoint exist-notes-link")
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

        logger.info("endpoint exist-notes-link: response 200")
        return jsonify(chat_data)

    except Exception as e:
        logger.error("Поймали исключение")
        logger.error(f"Ошибка: {e}")
        return abort(400, e)


@app.route('/delete-notes-link', methods=['DELETE'])
def delete_notes_link():
    try:
        logger.info("endpoint delete-notes-link")
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
