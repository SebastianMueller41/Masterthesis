import subprocess
import os
import sys
import tempfile

def call_sat_solver(script_path, filepath, option='h'):
    """Call the SAT solver script and return the output."""
    try:
        result = subprocess.run(
            [sys.executable, script_path, filepath, option], 
            capture_output=True, 
            text=True,
            check=True  # Ensures any subprocess errors are caught
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error calling SAT solver: {e}")

    output_lines = result.stdout.splitlines()
    for line in output_lines:
        if line.startswith("o "):
            return int(line.split()[1])
    raise ValueError("Failed to obtain inconsistency measure from SAT solver.")

def calculate_inconsistency(filepath, script_path='sat4im/src/sat4im.py'):
    initial_inconsistency_measure = call_sat_solver(script_path, filepath)

    with open(filepath, 'r') as file:
        lines = file.readlines()

    print(f"Initial inconsistency measure: {initial_inconsistency_measure}")
    print("File content:")
    for line in lines:
        print(line, end='')

    inconsistency_differences = []
    for i in range(len(lines)):
        # Create a temporary file for the modified dataset
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.writelines(lines[:i] + lines[i+1:])
            temp_filepath = temp_file.name

        inconsistency_measure = call_sat_solver(script_path, temp_filepath)
        inconsistency_difference = initial_inconsistency_measure - inconsistency_measure
        inconsistency_differences.append(inconsistency_difference)

        # Clean up: Delete the temporary dataset file
        os.remove(temp_filepath)

    print(f"\nList of inconsistency measures: {inconsistency_differences}")
    return inconsistency_differences
