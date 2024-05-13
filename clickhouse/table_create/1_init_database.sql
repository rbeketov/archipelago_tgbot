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
ORDER BY (timestamp, chat_id)
TTL timestamp + INTERVAL 7 DAY;


CREATE TABLE IF NOT EXISTS notes_chat_relations (
    note_id String,
    chat_name String,
    chat_id Int64
) ENGINE = MergeTree
ORDER BY note_id
PRIMARY KEY note_id;

CREATE TABLE IF NOT EXISTS tg_chat_summary (
    chat_id Int64,
    note_id String,
    summary String,
    role_ String,
    detail_degree String,
    timestamp_last_message DateTime('Etc/UTC'),
    timestamp DateTime('Etc/UTC') DEFAULT now()
) ENGINE = MergeTree
ORDER BY (timestamp, chat_id) DESC
TTL timestamp + INTERVAL 7 DAY;

