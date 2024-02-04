   """
    solver_type = sys.argv[1].lower()
    
    if solver_type == "minisat":
        # Convert dataset to CNF for MiniSat
        cnf_filename = os.path.join(output_directory, generate_output_filename(os.path.basename(dataset_filepath)))
        kb = parse.KnowledgeBase(open(dataset_filepath).read().split("\n"), file_format="pl")
        parse.write_cnf_to_file(kb, cnf_filename)
        print(f"CNF data saved to {os.path.abspath(cnf_filename)}")

        # Run MiniSat on the CNF file
        minisat_output_filename = cnf_filename + '_result' #cnf_filename.replace('.cnf', '_minisat.result')
        run_minisat(cnf_filename, minisat_output_filename)
        print(f"MiniSat result saved to {os.path.abspath(minisat_output_filename)}")
    else:
        print("Invalid solver type. Please choose 'minisat'.")
        sys.exit(1)

    def run_minisat(cnf_filename, output_filename):
        subprocess.run(['minisat', cnf_filename, output_filename])
    """