CREATE DATABASE IF NOT EXISTS yavka_tgbot;

USE yavka_tgbot;

CREATE TABLE IF NOT EXISTS tg_messages (
    chat_id Int64,
    id_message Int64,
    message_ String,
    speaker String,
    reply String,
    timestamp DateTime('Etc/UTC')
) ENGINE = MergeTree
ORDER BY (chat_id, timestamp)
TTL timestamp + INTERVAL 7 DAY;


CREATE TABLE IF NOT EXISTS notes_chat_relations (
    note_id Int64,
    chat_id Int64
) ENGINE = MergeTree
ORDER BY note_id
PRIMARY KEY note_id;
