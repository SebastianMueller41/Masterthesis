#!/bin/bash

# Path to your CSV file with filenames
FILENAME_LIST="sig3_5_15.csv"

# Path to your Python script
PYTHON_SCRIPT="main.py"

# Other fixed arguments
STRATEGY_PARAM=0
METHOD="-k"
ALPHA="A0&&!A0"
LOG_DB="--log-db"

# Read each line in the filename list
while IFS=, read -r FILENAME
do
  # Skip the header line if present
  if [ "$FILENAME" != "filename" ]; then
    # Run the Python script with the current filename and other arguments
    python "$PYTHON_SCRIPT" "$FILENAME" "$STRATEGY_PARAM" "$METHOD" --alpha "$ALPHA" "$LOG_DB"
  fi
done < "$FILENAME_LIST"
