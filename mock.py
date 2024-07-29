import os
import subprocess
import sys
import logging
from src.structs.dataset import DataSet

from src.CNFconverter.parse import CNFConverter
from src.structs import dataset
from src.structs.dataset import initialize_dataset

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
kr_logger = logging.getLogger(__name__)

def cn(B_dataset, alpha):
    temp_dir = "tmp"
    temp_file = os.path.join(temp_dir, "temp_database.txt")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    B_copy = B_dataset.clone()
    B_copy.add_element("!(" + alpha + ")")
    B_copy.to_file(temp_file)
    
    converter = CNFConverter(verbose=False)
    converter.convert_to_cnf(temp_file, temp_file)
    
    # Log the contents of the temp file
    with open(temp_file, 'r') as file:
        temp_file_contents = file.read()
    kr_logger.debug(f"Contents of {temp_file}:\n{temp_file_contents}")
    
    result = subprocess.run(['minisat', temp_file], capture_output=True, text=True)
    output = result.stdout
    error_output = result.stderr
    
    kr_logger.debug(f"MiniSat stdout:\n{output}")
    if error_output:
        kr_logger.debug(f"MiniSat stderr:\n{error_output}")
    
    last_line = output.splitlines()[-1] if output.splitlines() else ""
    
    if "UNSAT" in last_line:
        kr_logger.debug(f"MiniSat result: UNSAT. Therefore, {alpha} is in Cn({B_dataset.get_elements()})")
        return True
    elif "SAT" in last_line:
        kr_logger.debug(f"MiniSat result: SAT. Therefore, {alpha} is not in Cn({B_dataset.get_elements()})")
        return False
    else:
        print("MiniSat output was unexpected.")
        kr_logger.debug("MiniSat output was unexpected.")
        sys.exit(1)

dataset.load_elements_from_file('tmp/example.txt')

B_dataset = DataSet(dataset.ini_elements)

alpha = "(A0&&!A0)"

result = cn(B_dataset, alpha)
print(f"Result: {result}")
