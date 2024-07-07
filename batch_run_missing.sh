#!/bin/bash

# Path to your Python script
PYTHON_SCRIPT="main.py"

# Array of missing combinations CSV files
MISSING_COMBINATIONS_FILES=(
    "data/SRS/missing_combinations_3_5_15.csv"
    "data/SRS/missing_combinations_5_15_25.csv"
    "data/SRS/missing_combinations_10_15_25.csv"
)

# Loop through each missing combinations CSV file
for MISSING_COMBINATIONS_FILE in "${MISSING_COMBINATIONS_FILES[@]}"
do
  # Check if the file exists
  if [ ! -f "$MISSING_COMBINATIONS_FILE" ]; then
    echo "File not found: $MISSING_COMBINATIONS_FILE"
    continue
  fi

  # Read each line in the missing combinations file, ignore additional columns
  while IFS=, read -r FILE_NAME DATASET DIV_CONQ SW_SIZE STRATEGY_PARAM _REST
  do
    # Skip the header line
    if [ "$FILE_NAME" != "file_name" ]; then
      # Construct the parameter set
      PARAM_SET="--alpha A0&&!A0 --log-db"
      if [ "$DIV_CONQ" -eq 1 ]; then
        PARAM_SET="$PARAM_SET -dc"
      fi
      PARAM_SET="$PARAM_SET --sw-size $SW_SIZE"

      echo "Processing $FILE_NAME with strategy $STRATEGY_PARAM and params $PARAM_SET"
      python "$PYTHON_SCRIPT" "$FILE_NAME" "$STRATEGY_PARAM" -k $PARAM_SET
    fi
  done < "$MISSING_COMBINATIONS_FILE"
done
