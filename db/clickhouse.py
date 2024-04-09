import os


import clickhouse_connect
from clickhouse_connect import common
from dotenv import load_dotenv


HOST = "HOST_CLICK"
PORT = "PORT_CLICK"
DATABASE = "DATABASE_CLICK"


class SingleTone(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class ClickClient(metaclass=SingleTone):
    def __init__(self):
        load_dotenv()

        common.set_setting('autogenerate_session_id', False)

        self._host = os.environ.get(HOST)
        self._port = os.environ.get(PORT)
        self._database = os.environ.get(DATABASE)
        self._click_client = clickhouse_connect.get_client(
            host=self._host,
            port=self._port,
            username='default',
            database=self._database,
        )

    def insert_new_message(
        self,
        chat_id: int,
        id_message: int,
        message_: str,
        speaker: str,
        reply: str,
        timestamp: int,
    ):
        data = [[chat_id, id_message, message_, speaker, reply, timestamp]]
        self._click_client.insert(
            'tg_messages',
            data,
            column_names=[
                'chat_id',
                'id_message',
                'message_',
                'speaker',
                'reply',
                'timestamp'
            ]
        )

    def get_chat_message(
        self,
        chat_id: int,
    ):
        query_ = f"SELECT * FROM tg_messages WHERE chat_id = {chat_id}"
        q = self._click_client.query(query_)
        res = q.result_rows
        q.close()
        return res

    def insert_or_update_token(
        self,
        note_token: str,
        chat_id: int,
    ):
        query_ = f"SELECT * FROM notes_chat_relations WHERE note_id = {note_token}"
        result_select = self._click_client.query(query_).result_rows
        if result_select:
            query_upd = f"UPDATE notes_chat_relations SET chat_id = {chat_id} WHERE note_id = {note_token};"
            q = self._click_client.query(query_upd)
            q.close()
        else:
            data = [[note_token, chat_id]]
            self._click_client.insert(
                'notes_chat_relations',
                data,
                column_names=[
                    'note_id',
                    'chat_id'
                ]
            )

    def get_chat_id_for_token(
        self,
        note_token: int,
    ):
        query_ = f"SELECT * FROM notes_chat_relations WHERE note_id = {note_token}"
        q = self._click_client.query(query_)
        result_rows = q.result_rows
        q.close()
        if result_rows:
            return result_rows[0][-1]
        return None
