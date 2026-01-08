#!/bin/bash
# Script to run the ETL pipeline using the virtual environment automatically

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the python script using the venv's python executable
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/etl_pipeline.py"
