import csv
import subprocess

# Path to your main.py script
PYTHON_SCRIPT = "main.py"

# List of CSV files containing missing combinations
MISSING_COMBINATION_FILES = [
    #'data/SRS/sig3_5_15.csv',
    'data/SRS/sig5_15_25.csv',
    'data/SRS/sig10_15_25.csv'
    # Add more CSV file paths as needed
]

# Function to execute the command
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        print("Command failed with exit code", e.returncode)

# Strategy parameters
STRATEGY_PARAMS = [3]

# Parameter sets
PARAMETER_SETS = [
    "--alpha '(A0&&!A0)' -path-db -res-db",
    # Add more parameter sets if needed
]

# Loop through each CSV file
for MISSING_COMBINATIONS_FILE in MISSING_COMBINATION_FILES:
    # Read the CSV file and process each row
    with open(MISSING_COMBINATIONS_FILE, mode='r') as file:
        reader = csv.reader(file)
        first_line = next(reader)  # Read the first line
        if first_line[0] == 'filename':
            # Skip the header row if it matches 'filename'
            pass
        else:
            # If the first row is not the header, process it
            FILE_NAME, *_ = first_line
            for strategy_param in STRATEGY_PARAMS:
                if strategy_param == 3:
                    search_strategies = ["P", "V"]
                else:
                    search_strategies = ["P"]
                for search_strategy in search_strategies:
                    for param_set in PARAMETER_SETS:
                        command = f"python3 {PYTHON_SCRIPT} '{FILE_NAME}' --sp {strategy_param} --ss {search_strategy} {param_set}"
                        print(f"Executing: {command}")
                        execute_command(command)

        for row in reader:
            FILE_NAME, *_ = row
            for strategy_param in STRATEGY_PARAMS:
                if strategy_param == 3:
                    search_strategies = ["P", "V"]
                else:
                    search_strategies = ["P"]
                for search_strategy in search_strategies:
                    for param_set in PARAMETER_SETS:
                        command = f"python3 {PYTHON_SCRIPT} '{FILE_NAME}' --sp {strategy_param} --ss {search_strategy} {param_set}"
                        print(f"Executing: {command}")
                        execute_command(command)
