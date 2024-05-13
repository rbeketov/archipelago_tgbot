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

    def get_last_summarize_by_chat_id(
        self,
        chat_id: int,
    ):
        query_ = f"SELECT summary, timestamp_last_message FROM tg_chat_summary WHERE chat_id = {chat_id} LIMIT 1"
        q = self._click_client.query(query_)
        res = q.result_rows
        q.close()
        return res
    
    def insert_new_summarization(
        self,
        chat_id: int,
        note_id: str,
        summary: str,
        timestamp_last_message: int,
    ):
        data = [[chat_id, note_id, summary, timestamp_last_message]]
        self._click_client.insert(
            'tg_chat_summary',
            data,
            column_names=[
                'chat_id',
                'note_id',
                'summary',
                'timestamp_last_message',
            ]
        )

    def insert_or_update_token(
        self,
        note_token: str,
        chat_id: int,
        chat_name: str,
    ):
        query_ = f"SELECT * FROM notes_chat_relations WHERE note_id = '{note_token}'"
        q = self._click_client.query(query_)
        result_select = q.result_rows
        q.close()
        if result_select:
            query_upd = f"UPDATE notes_chat_relations SET chat_id = {chat_id}, chat_name = {chat_name} WHERE note_id = '{note_token}';"
            q = self._click_client.query(query_upd)
            q.close()
        else:
            data = [[note_token, chat_id, chat_name]]
            self._click_client.insert(
                'notes_chat_relations',
                data,
                column_names=[
                    'note_id',
                    'chat_id',
                    'chat_name',
                ]
            )

    def get_chat_id_for_token(
        self,
        note_token: str,
    ):
        query_ = f"SELECT chat_id FROM notes_chat_relations WHERE note_id = '{note_token}';"
        q = self._click_client.query(query_)
        result_rows = q.result_rows
        print(result_rows)
        q.close()
        if result_rows:
            return result_rows[0][-1]
        return None
    
    def get_chat_data_for_token(
        self,
        note_token: str,
    ):
        query_ = f"SELECT chat_id, chat_name FROM notes_chat_relations WHERE note_id = '{note_token}';"
        q = self._click_client.query(query_)
        result_rows = q.result_rows
        q.close()
        
        if result_rows:
            return {
                "chat_id": result_rows[0][0],
                "chat_name": result_rows[0][1],
            }
        return None

    def delete_token_link(
        self,
        note_token: str,
    ):
        chat_id = self.get_chat_id_for_token(note_token)
        if not chat_id:
            return False
        query_ = f"ALTER TABLE notes_chat_relations DELETE WHERE note_id = '{note_token}';" 
        q = self._click_client.query(query_)
        q.close()
        return True