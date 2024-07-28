#!/bin/bash

# Path to your Python script
PYTHON_SCRIPT="sat4im/src/sat4im.py"

# CSV file containing filenames
CSV_FILE="data/SRS/sig5_15_25.csv"

# Output results file
RESULTS_FILE="tmp/results_con.txt"

# Check if the CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "CSV file not found: $CSV_FILE"
    exit 1
fi

# Create the results file or clear it if it already exists
: > "$RESULTS_FILE"

# Read the CSV file and execute the Python script for each filename
while IFS=, read -r FILE_NAME _; do
    if [ "$FILE_NAME" != "filename" ]; then
        echo "Processing file: $FILE_NAME"
        python3 "$PYTHON_SCRIPT" "$FILE_NAME" c > tmp/output.txt
        if [ $? -ne 0 ]; then
            echo "Command failed with exit code $?"
        else
            while IFS= read -r line; do
                if [[ $line == o* ]]; then
                    num=$(echo "$line" | awk '{print $2}')
                    if (( num == 0 )); then
                        echo "$FILE_NAME: $line" >> "$RESULTS_FILE"
                    fi
                fi
            done < tmp/output.txt
        fi
    fi
done < "$CSV_FILE"
