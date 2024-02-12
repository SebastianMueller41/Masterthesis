"""
This module defines a class for converting a given knowledge base into Conjunctive Normal Form (CNF)
and writing the result into an output file. The input and output filenames are specified via command line
arguments, along with an optional flag to control console output verbosity.
"""

import sys
from .core import KnowledgeBase

class CNFConverter:
    def __init__(self, verbose=False):
        """
        Initialize the CNFConverter with an option to enable or disable verbose output.

        Args:
            verbose (bool): If True, enables printing of CNF to the console. Default is False.
        """
        self.verbose = verbose

    def generate_output_filename(self, input_filename):
        """
        Generate a default output filename based on the input filename.

        Args:
            input_filename (str): The name of the input file.

        Returns:
            str: The name of the output file with '_result.cnf' appended.
        """
        return f"{input_filename}_result.cnf"

    def convert_to_cnf(self, input_filename, output_filename=None):
        """
        Read the knowledge base from the input file, convert it to CNF, and write to the output file.
        Optionally, print the CNF to the console based on the verbosity setting.

        Args:
            input_filename (str): The path to the input file containing the knowledge base.
            output_filename (str, optional): The path to the output file for the CNF result. If not provided,
                                             a default name is generated based on the input filename.
        """
        if output_filename is None:
            output_filename = self.generate_output_filename(input_filename)

        kb = KnowledgeBase(open(input_filename).read().split("\n"))
        clauses, lits = kb.to_group_cnf()

        n_vars = next(kb.var_counter)-1
        n_clauses = len(clauses) + len(lits)

        if self.verbose:
            print("p cnf", n_vars, n_clauses)
            for clause in clauses:
                print(" ".join(map(str, clause)) + " 0")
            for lit in lits:
                print(str(lit) + " 0")

        with open(output_filename, 'w') as file:
            file.write(f"p cnf {n_vars} {n_clauses}\n")
            for clause in clauses:
                file.write(" ".join(map(str, clause)) + " 0\n")
            for lit in lits:
                file.write(str(lit) + " 0\n")

        print(f"CNF format saved to {output_filename}" if self.verbose else "")

# Check for proper command line arguments and initialize CNFConverter
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_filename> [<output_filename>] [--verbose]")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    verbose = '--verbose' in sys.argv

    converter = CNFConverter(verbose=verbose)
    converter.convert_to_cnf(input_filename, output_filename)
