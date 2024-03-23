CREATE DATABASE IF NOT EXISTS yavka;

USE yavka;

CREATE TABLE IF NOT EXISTS tg_messages (
    id UInt32,
    reply_id Nullable(UInt32),
    chat_id UInt32,
    speaker UInt32,
    reply message String,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY
    (chat_id, timestamp) TTL timestamp + INTERVAL 7 DAY;

CREATE TABLE chat_account_relations (chat_id UInt32, tg_account_id UInt32) ENGINE = MergeTree()
ORDER BY
    (chat_id, tg_account_id);