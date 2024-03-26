#!/bin/bash

# should be executed in py venv
# should be executed in with sudo

if [ -z "${SERVICE_NAME}" ]; then 
    exit 1
fi
