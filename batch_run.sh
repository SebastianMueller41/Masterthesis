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

# Strategy parameters and pruner combinations
declare -A STRATEGY_PRUNER_COMBINATIONS=(
    [1]="LOWER"
    [2]="LOWER UPPER"
    [3]="UPPER"
)


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
    if [ -f "$MISSING_COMBINATIONS_FILE" ]; then
        while IFS=, read -r FILE_NAME _; do
            if [ "$FILE_NAME" != "filename" ]; then
                for strategy_param in "${!STRATEGY_PRUNER_COMBINATIONS[@]}"; do
                    pruner_options=(${STRATEGY_PRUNER_COMBINATIONS[$strategy_param]})
                    for pruner_option in "${pruner_options[@]}"; do
                        for search_strategy in "${SEARCH_STRATEGIES[@]}"; do
                            for param_set in "${PARAMETER_SETS[@]}"; do
                                for expand_option in "${EXPAND_OPTIONS[@]}"; do
                                    for shrink_option in "${SHRINK_OPTIONS[@]}"; do
                                        command="python3 $PYTHON_SCRIPT '$FILE_NAME' --sp $strategy_param --ss $search_strategy --pruner $pruner_option $expand_option $shrink_option $param_set"
                                        execute_command "$command"
                                    done
                                done
                            done
                        done
                    done
                done
            fi
        done < "$MISSING_COMBINATIONS_FILE"
    fi
done
