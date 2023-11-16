import sys
import subprocess
import os
import parse

print("Current Working Directory:", os.getcwd())

def run_open_wbo(wcnf_filename, output_filename):
    open_wbo_path = "open-wbo/open-wbo" 
    print("TEST!")
    subprocess.run([open_wbo_path, wcnf_filename, output_filename])

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
    wcnf_filename = os.path.join(output_directory, normalized_path + '.wcnf')
    kb = parse.KnowledgeBase(open(dataset_filepath).read().split("\n"))
    parse.write_wcnf_to_file(kb, wcnf_filename)
    print(f"WCNF data saved to {os.path.abspath(wcnf_filename)}")  # Print the absolute path

    print("WCNF File Path:", wcnf_filename)

    if solver_type == "maxsat":
        # Run Open-WBO on the WCNF file
        open_wbo_output_filename = os.path.join(output_directory, 'maxsat.result')
        # open_wbo_output_filename = os.path.join(output_directory, normalized_path + '_openwbo.result')
        run_open_wbo(wcnf_filename, open_wbo_output_filename)
        print(f"Open-WBO result saved to {os.path.abspath(open_wbo_output_filename)}")  # Print the absolute path
    elif solver_type == "minisat":
        # Convert WCNF to CNF for MiniSat
        cnf_filename = os.path.join(output_directory, normalized_path + '_converted.cnf')
        parse.convert_wcnf_to_cnf(wcnf_filename, cnf_filename)
        print(f"CNF data converted and saved to {os.path.abspath(cnf_filename)}")  # Print the absolute path

        # Run MiniSat on the converted CNF file
        minisat_output_filename = cnf_filename.replace('.cnf', '_minisat.result')
        run_minisat(cnf_filename, minisat_output_filename)
        print(f"MiniSat result saved to {os.path.abspath(minisat_output_filename)}")  # Print the absolute path
    else:
        print("Invalid solver type. Please choose 'minisat' or 'maxsat'.")
        sys.exit(1)
