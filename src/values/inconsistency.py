import subprocess
import os
import sys
import tempfile
import math
from itertools import chain, combinations

def call_sat_solver(script_path, subset, option='sum'):
    """Call the SAT solver script and return the output using a subset."""
    # Write the subset to a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write('\n'.join(subset))
        temp_filepath = temp_file.name

    try:
        result = subprocess.run(
            [sys.executable, script_path, temp_filepath, option], 
            capture_output=True, 
            text=True,
            check=True  # Ensures any subprocess errors are caught
        )
        os.remove(temp_filepath)  # Clean up the temporary file
    except subprocess.CalledProcessError as e:
        os.remove(temp_filepath)  # Ensure the temporary file is removed even on error
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
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.writelines(lines[:i] + lines[i+1:])
            temp_filepath = temp_file.name

        inconsistency_measure = call_sat_solver(script_path, temp_filepath)
        inconsistency_difference = initial_inconsistency_measure - inconsistency_measure
        inconsistency_differences.append(inconsistency_difference)

        os.remove(temp_filepath)

    print(f"\nList of inconsistency measures: {inconsistency_differences}")
    return inconsistency_differences

def powerset(s):
    "Generate all combinations of the elements in set s."
    s = list(s)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def powerset_to_file(iterable, filename):
    """Generate all non-empty subsets of an iterable and write each to a new line in a file."""
    s = list(iterable)
    subsets = (','.join(map(str, combo)) for combo in chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1)))
    
    with open(filename, 'w') as file:
        for subset in subsets:
            file.write(subset + '\n')

def calculate_all_inconsistency_values(dataset, sat_solver_script='sat4im/src/sat4im.py'):
    inconsistency_values = {}
    all_subsets = list(powerset(dataset))  # Convert generator to list
    powerset_length = 2 ** len(dataset)  # Calculate the total number of subsets
    print(f"Total number of subsets (Powerset length): {powerset_length}")
    print(f"Powersets: {all_subsets}")  # Print all subsets once
    for subset in all_subsets:
        #print(f"Subset: {subset}")
        inconsistency_values[subset] = call_sat_solver(sat_solver_script, subset)
    return inconsistency_values

def compute_shapley_values(dataset, inconsistency_values):
    shapley_values = {formula: 0 for formula in dataset}
    total_elements = len(dataset)
    
    for formula in dataset:
        for subset in powerset(dataset):
            if formula in subset:
                subset_without_formula = tuple(x for x in subset if x != formula)
                marginal_contribution = (
                    inconsistency_values[subset] -
                    inconsistency_values.get(subset_without_formula, 0)
                )
                weight = (math.factorial(len(subset_without_formula)) * 
                          math.factorial(total_elements - len(subset_without_formula) - 1) /
                          math.factorial(total_elements))
                shapley_values[formula] += weight * marginal_contribution
    
    for formula in dataset:
        shapley_values[formula] /= total_elements
    return shapley_values
