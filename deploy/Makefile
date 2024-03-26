PROJECT_DIR ?= /home/ubuntu/tg_bot

tg_bot/start:
	sudo systemctl start tg_bot

tg_bot/demonize:
	SERVICE=tg_bot PROJECT_DIR=${PROJECT_DIR} /bin/sh daemon.sh

tg_bot/logs:
	journalctl -u tg_bot.service

chat_summarize/start:
	sudo systemctl start chat_summarize

chat_summarize/demonize:
	SERVICE=chat_summarize PROJECT_DIR=${PROJECT_DIR} sudo /bin/sh daemon.sh

chat_summarize/logs:
	journalctl -u chat_summarize.service
