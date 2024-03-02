import subprocess
import os, sys

def calculate_inconsistency(filepath, script_path='sat4im/src/sat4im.py'):

    #Debugging prints
    print(f"script_path: {script_path}")  # Ensure this is not None
    print(f"filepath: {filepath}")  # Ensure this is not None

    # Run the subprocess for the entire dataset first to get the initial inconsistency measure
    initial_result = subprocess.run([sys.executable, script_path, filepath, 'h'], capture_output=True, text=True)
    output_lines = initial_result.stdout.splitlines()
    initial_inconsistency_measure = None
    for line in output_lines:
        if line.startswith("o "):
            initial_inconsistency_measure = int(line.split()[1])
            break
    if initial_inconsistency_measure is None:
        sys.exit("Failed to obtain initial inconsistency measure. No dataset found.")

    # Read the dataset from the file
    with open(filepath, 'r') as file:
        lines = file.readlines()

    print("Initial inconsistency measure:", initial_inconsistency_measure)
    print("File content:")
    for line in lines:
        print(line, end='')

    print("")

    inconsistency_differences = []

    for i in range(len(lines)):
        # Remove the current line and save to a temporary file
        modified_lines = lines[:i] + lines[i+1:]
        temp_filepath = 'temp_dataset.txt'
        with open(temp_filepath, 'w') as temp_file:
            temp_file.writelines(modified_lines)

        # Call the external script with the modified dataset
        result = subprocess.run([sys.executable, script_path, temp_filepath, 'h'], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()

        # Search for the line starting with 'o' and extract the number
        inconsistency_measure = None
        for line in output_lines:
            if line.startswith("o "):
                inconsistency_measure = int(line.split()[1])
                break

        if inconsistency_measure is not None:
            # Calculate the difference in inconsistency value due to the removal of the current line
            inconsistency_difference = initial_inconsistency_measure - inconsistency_measure
            inconsistency_differences.append(inconsistency_difference)
        else:
            inconsistency_differences.append("Error: Could not calculate")

        # Clean up: Delete the temporary dataset file
        os.remove(temp_filepath)

    """
    # Print the inconsistency differences
    for index, difference in enumerate(inconsistency_differences):
        print(f"Inconsistency difference for line {index + 1}: {difference}")
    """

    print(f"List of inconsistency measures: {inconsistency_differences}\n")
    return inconsistency_differences
