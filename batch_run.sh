#!/bin/bash

# Array of CSV files with filenames
FILENAME_LISTS=(
    "data/SRS/sig3_5_15.csv"
    "data/SRS/sig5_15_25.csv"
    "data/SRS/sig10_15_15.csv"
    "data/SRS/sig15_15_25.csv"
    "data/SRS/sig15_25_50.csv"
)

# Path to your Python script
PYTHON_SCRIPT="main.py"

# Array of strategy parameters
STRATEGY_PARAMS=(0 1 2 4)

# Array of parameter sets
PARAMETER_SETS=(
    "--alpha A0&&!A0 --log-db -dc"
    "--alpha A0&&!A0 --log-db -dc --sw-size 5"
    "--alpha A0&&!A0 --log-db -dc --sw-size 10"
)

# Loop through each CSV file
for FILENAME_LIST in "${FILENAME_LISTS[@]}"
do
  # Check if the file exists
  if [ ! -f "$FILENAME_LIST" ]; then
    echo "File not found: $FILENAME_LIST"
    continue
  fi
  
  # Read each line in the filename list
  while IFS=, read -r FILENAME
  do
    # Skip the header line if present
    if [ "$FILENAME" != "filename" ]; then
      # Run the Python script with the current filename, strategy parameters, and each set of additional parameters
      for STRATEGY_PARAM in "${STRATEGY_PARAMS[@]}"
      do
        for PARAM_SET in "${PARAMETER_SETS[@]}"
        do
          echo "Processing $FILENAME with strategy $STRATEGY_PARAM and params $PARAM_SET from $FILENAME_LIST"
          python "$PYTHON_SCRIPT" "$FILENAME" "$STRATEGY_PARAM" -k $PARAM_SET
        done
      done
    fi
  done < "$FILENAME_LIST"
done
