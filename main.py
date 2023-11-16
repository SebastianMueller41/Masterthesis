import sys
import subprocess
import os
import parse

def run_open_wbo(wcnf_filename, output_filename):
    open_wbo_path = "/path/to/open-wbo"  # Replace with the actual path to the open-wbo executable
    subprocess.run([open_wbo_path, wcnf_filename, "-o", output_filename])

def run_minisat(cnf_filename, output_filename):
    subprocess.run(['minisat', cnf_filename, output_filename])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <solver_type> <dataset_file>")
        print("solver_type: minisat or maxsat")
        sys.exit(1)

    solver_type = sys.argv[1].lower()
    dataset_filepath = sys.argv[2]
    normalized_path = parse.normalize_path(dataset_filepath)
    output_directory = 'Results'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Generate WCNF file
    wcnf_filename = os.path.join(output_directory, normalized_path + '_output.wcnf')
    kb = parse.KnowledgeBase(open(dataset_filepath).read().split("\n"))
    parse.write_wcnf_to_file(kb, wcnf_filename)
    print(f"WCNF data saved to {wcnf_filename}")

    if solver_type == "maxsat":
        # Run Open-WBO on the WCNF file
        open_wbo_output_filename = os.path.join(output_directory, normalized_path + '_openwbo.result')
        run_open_wbo(wcnf_filename, open_wbo_output_filename)
        print(f"Open-WBO result saved to {open_wbo_output_filename}")
    elif solver_type == "minisat":
        # Convert WCNF to CNF for MiniSat
        cnf_filename = os.path.join(output_directory, normalized_path + '_converted.cnf')
        parse.convert_wcnf_to_cnf(wcnf_filename, cnf_filename)
        print(f"CNF data converted and saved to {cnf_filename}")

        # Run MiniSat on the converted CNF file
        minisat_output_filename = cnf_filename.replace('.cnf', '_minisat.result')
        run_minisat(cnf_filename, minisat_output_filename)
        print(f"MiniSat result saved to {minisat_output_filename}")
    else:
        print("Invalid solver type. Please choose 'minisat' or 'maxsat'.")
        sys.exit(1)
