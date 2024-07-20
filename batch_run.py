import csv
import subprocess

# Path to your main.py script
PYTHON_SCRIPT = "main.py"

# Path to the CSV file containing missing combinations
MISSING_COMBINATIONS_FILE = 'data/SRS/sig20_25_50.csv'
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
    first_line = next(reader)  # Read the first line
    if first_line[0] == 'filename':
        # Skip the header row if it matches 'filename'
        pass
    else:
        # If the first row is not the header, process it
        FILE_NAME, *_ = first_line
        command = f"python3 {PYTHON_SCRIPT} '{FILE_NAME}' --sp 3 --ss P -path-db --alpha 'A0&&!A0'"
        print(f"Executing: {command}")
        execute_command(command)

    for row in reader:
        FILE_NAME, *_ = row
        command = f"python3 {PYTHON_SCRIPT} '{FILE_NAME}' --sp 3 --ss P -path-db --alpha 'A0&&!A0'"
        print(f"Executing: {command}")
        execute_command(command)
