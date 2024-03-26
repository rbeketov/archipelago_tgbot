PROJECT_DIR ?= /home/ubuntu/tg_bot

tg_bot/start:
	sudo systemctl start tg_bot

tg_bot/demonize:
	SERVICE=tg_bot PROJECT_DIR=${PROJECT_DIR} /bin/sh daemon.sh

chat_summarize/start:
	sudo systemctl start chat_summarize

chat_summarize/demonize:
	SERVICE=chat_summarize PROJECT_DIR=${PROJECT_DIR} sudo /bin/sh daemon.sh
