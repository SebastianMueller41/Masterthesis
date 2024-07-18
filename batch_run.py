import csv
import subprocess

# Path to your main.py script
PYTHON_SCRIPT = "main.py"

# Path to the CSV file containing missing combinations
MISSING_COMBINATIONS_FILE = 'data/SRS/sig3_5_15.csv'
# "data/missing_combinations_ARG.csv"

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
    #next(reader)  # Skip the header row

    for row in reader:
        FILE_NAME, *_ = row

        command = f"python3 {PYTHON_SCRIPT} '{FILE_NAME}' --sp 3 -r -res-db --ss P -path-db --alpha 'A0&&!A0'"
        print(f"Executing: {command}")
        execute_command(command)
