"""
This script converts a given knowledge base into Conjunctive Normal Form (CNF)
and writes the result into an output file. The input and output filenames are
specified via command line arguments.
"""

import sys
from core import KnowledgeBase

def generate_output_filename(input_filename):
    """
    Generate a default output filename based on the input filename.

    Args:
        input_filename (str): The name of the input file.

    Returns:
        str: The name of the output file with '_result.cnf' appended.
    """
    return f"{input_filename}_result.cnf"


# Check for proper command line arguments
if len(sys.argv) <= 1:
    print("Usage: python script.py <input_filename> [<output_filename>]")
    sys.exit(1)

input_filename = sys.argv[1]
output_filename = sys.argv[2] if len(sys.argv) > 2 else generate_output_filename(input_filename)

# Read the knowledge base from the input file and convert it to CNF
kb = KnowledgeBase(open(input_filename).read().split("\n"))
clauses, lits = kb.to_group_cnf()

# Calculate the number of variables and clauses for the CNF header
n_vars = next(kb.var_counter)-1
n_clauses = len(clauses) + len(lits)

# Print the CNF to the console
print("p cnf", n_vars, n_clauses)
for clause in clauses:
    print(" ".join(map(str, clause)) + " 0")
for lit in lits:
    print(str(lit) + " 0")

# Write the CNF to the output file
with open(output_filename, 'w') as file:
    file.write(f"p cnf {n_vars} {n_clauses}\n")
    for clause in clauses:
        file.write(" ".join(map(str, clause)) + " 0\n")
    for lit in lits:
        file.write(str(lit) + " 0\n")

# print(f"CNF format saved to {output_filename}")
