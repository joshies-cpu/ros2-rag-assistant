#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run uvicorn using the venv's executable
"$SCRIPT_DIR/venv/bin/uvicorn" main_api:app --reload --host 127.0.0.1 --port 8000
