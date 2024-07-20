#!/bin/bash
set -x

# Path to your Python script
PYTHON_SCRIPT="main.py"

# Array of missing combinations CSV files
MISSING_COMBINATIONS_FILES=(
    "data/missing_combinations_ARG.csv"
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
  # Skip the first line (header)
  tail -n +2 "$MISSING_COMBINATIONS_FILE" | while IFS=, read -r FILE_NAME DIV_CONQ SW_SIZE STRATEGY_PARAM _REST
  do
    # Construct the parameter set
    PARAM_SET="--alpha 'arg_0&&!arg_0' -log-db --ss P -path-db"  # Changed --log-db to -log-db and added --ss P and -path-db as default
    if [ "$DIV_CONQ" -eq 1 ]; then
      PARAM_SET="$PARAM_SET -dc"
    fi
    PARAM_SET="$PARAM_SET --sw-size $SW_SIZE"

    echo "Processing $FILE_NAME with strategy $STRATEGY_PARAM and params $PARAM_SET"
    
    # Full command
    COMMAND="python3 $PYTHON_SCRIPT $FILE_NAME --sp $STRATEGY_PARAM -k $PARAM_SET"
    echo "Executing: $COMMAND"
    
    # Execute the command and capture the output and error
    OUTPUT=$($COMMAND 2>&1)
    EXIT_CODE=$?

    echo "Output: $OUTPUT"
    if [ $EXIT_CODE -ne 0 ]; then
      echo "Error: Command failed with exit code $EXIT_CODE"
      echo "Full command: $COMMAND"
      exit $EXIT_CODE
    fi
  done
done
