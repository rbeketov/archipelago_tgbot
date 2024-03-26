#!/bin/bash

# should be executed in py venv
# should be executed in with sudo

if [ -z "${SERVICE}" ]; then
    echo "Specify SERVICE: (tg_bot, chat_summarize)"
    exit 1
fi

PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu}"
echo $PROJECT_DIR

pip install j2cli

export python_interpreter=$(which python)
export project_dir=$PROJECT_DIR
j2 ./${SERVICE}.service.j2 -e python_interpreter -e project_dir -o ${SERVICE}.service

sudo cp ${SERVICE}.service /etc/systemd/system/${SERVICE}.service

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE}.service
