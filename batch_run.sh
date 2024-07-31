#!/bin/bash

# Path to your main.py script
PYTHON_SCRIPT="main.py"

# List of CSV files containing missing combinations
MISSING_COMBINATION_FILES=(
    'sig3_vp0_NONE_DIVCONQ.csv'
    # Add more CSV file paths as needed
)

# Strategy parameters
STRATEGY_PARAMS=(1)

# Pruner options
PRUNER_OPTIONS=('NONE')

# Search strategies
SEARCH_STRATEGIES=('PBS')
#SEARCH_STRATEGIES=('BFS' 'DFS' 'HYS' 'PBS')

# Expand options
EXPAND_OPTIONS=(
    ''
    '--expand-sw-size 5'
    '--expand-sw-size 10'
    '--expand-sw-size 1'
    '--expand-div-conq'
)

# Shrink options
SHRINK_OPTIONS=(
    ''
    '--shrink-sw-size 5'
    '--shrink-sw-size 10'
    '--shrink-sw-size 1'
    '--shrink-div-conq 5'
)

# Parameter sets
PARAMETER_SETS=(
    "--alpha '(A0||A1)' -path-db -res-db"
    # Add more parameter sets if needed
)

# Function to execute the command
execute_command() {
    local command=$1
    echo "Executing: $command"
    eval $command
    if [ $? -ne 0 ]; then
        echo "Command failed with exit code $?"
    fi
}

# Loop through each CSV file
for MISSING_COMBINATIONS_FILE in "${MISSING_COMBINATION_FILES[@]}"; do
    echo "Processing file: $MISSING_COMBINATIONS_FILE"
    if [ -f "$MISSING_COMBINATIONS_FILE" ]; then
        while IFS=, read -r FILE_NAME _; do
            if [ "$FILE_NAME" != "filename" ]; then
                echo "Found file name: $FILE_NAME"
                for strategy_param in "${STRATEGY_PARAMS[@]}"; do
                    for pruner_option in "${PRUNER_OPTIONS[@]}"; do
                        for search_strategy in "${SEARCH_STRATEGIES[@]}"; do
                            for param_set in "${PARAMETER_SETS[@]}"; do
                                for expand_option in "${EXPAND_OPTIONS[@]}"; do
                                    for shrink_option in "${SHRINK_OPTIONS[@]}"; do
                                        command="python3 $PYTHON_SCRIPT '$FILE_NAME' --vp $strategy_param --ss $search_strategy --pruner $pruner_option $expand_option $shrink_option $param_set"
                                        echo "Command: $command"
                                        execute_command "$command"
                                    done
                                done
                            done
                        done
                    done
                done
            fi
        done < "$MISSING_COMBINATIONS_FILE"
    else
        echo "File not found: $MISSING_COMBINATIONS_FILE"
    fi
done
