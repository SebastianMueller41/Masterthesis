import csv
import subprocess

# Path to your main.py script
PYTHON_SCRIPT = "main.py"

# Path to the CSV file containing missing combinations
MISSING_COMBINATIONS_FILE = "data/missing_combinations_ARG.csv"

# Function to execute the command
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        print("Command failed with exit code", e.returncode)

# Read the CSV file and process each row
with open(MISSING_COMBINATIONS_FILE, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row

    for row in reader:
        FILE_NAME, DIV_CONQ, SW_SIZE, STRATEGY_PARAM, *_ = row
        PARAM_SET = "-res-db --ss P -path-db --alpha '(arg_0_0&&!arg_0_0)'"
        if int(DIV_CONQ) == 1:
            PARAM_SET += " -dc"
        PARAM_SET += f" --sw-size {SW_SIZE}"

        command = f"python3 {PYTHON_SCRIPT} {FILE_NAME} --sp {STRATEGY_PARAM} -k {PARAM_SET}"
        print(f"Executing: {command}")
        execute_command(command)
