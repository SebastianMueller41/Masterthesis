#!/bin/bash

# Path to your main.py script
PYTHON_SCRIPT="main.py"

# List of CSV files containing missing combinations
MISSING_COMBINATION_FILES=(
    'data/SRS/sig3_5_15.csv'
    #'data/SRS/sig5_15_25.csv'
    #'data/SRS/sig10_15_25.csv'
    #'data/SRS/SRS/Dataset_A/sig15_15_25.csv'
    # Add more CSV file paths as needed
)

# Strategy parameters and corresponding pruner combinations
STRATEGY_PARAMS=(3)
PRUNER_OPTIONS=('UPPER')

# Search strategies
SEARCH_STRATEGIES=('PBS')
# SEARCH_STRATEGIES=('BFS' 'DFS' 'HYS' 'PBS')

# Expand options
EXPAND_OPTIONS=('')
# EXPAND_OPTIONS=('--expand-div-conq' '--expand-sw-size 5' '--expand-sw-size 10')  # Add more if needed

# Shrink options
SHRINK_OPTIONS=('')
# SHRINK_OPTIONS=('--shrink-div-conq' '--shrink-sw-size 5' '--shrink-sw-size 10')  # Add more if needed

# Parameter sets
PARAMETER_SETS=(
    "--alpha '(A0&&!A0)' -path-db -res-db"
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
                for i in "${!STRATEGY_PARAMS[@]}"; do
                    strategy_param=${STRATEGY_PARAMS[$i]}
                    pruner_option=${PRUNER_OPTIONS[$i]}
                    echo "Using strategy_param: $strategy_param, pruner_option: $pruner_option"
                    for search_strategy in "${SEARCH_STRATEGIES[@]}"; do
                        echo "Using search_strategy: $search_strategy"
                        for param_set in "${PARAMETER_SETS[@]}"; do
                            echo "Using param_set: $param_set"
                            for expand_option in "${EXPAND_OPTIONS[@]}"; do
                                echo "Using expand_option: $expand_option"
                                for shrink_option in "${SHRINK_OPTIONS[@]}"; do
                                    echo "Using shrink_option: $shrink_option"
                                    command="python3 $PYTHON_SCRIPT '$FILE_NAME' --sp $strategy_param --ss $search_strategy --pruner $pruner_option $expand_option $shrink_option $param_set"
                                    echo "Command: $command"
                                    execute_command "$command"
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
