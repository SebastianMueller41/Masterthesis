import logging
import subprocess
from src.CNFconverter.parse import CNFConverter
from src.structs.dataset import DataSet

def expand(B_dataset, alpha, window_size):
    elements = B_dataset.get_elements()
    logging.info(f"{len(elements)} ELEMENTS: {elements}")
    B_prime = DataSet()
    counter = 0
    for start in range(0, len(elements), window_size):
        counter += 1
        if counter > len(elements) + 5:
            logging.warning("BREAK, MAX ITERATION, RETURNING NONE.")
            return None
        window_end = min(start + window_size, len(elements))
        window_elements = elements[start:window_end]
        for element in window_elements:
            B_prime.add_element(element)
        logging.debug(f"B_PRIME with {len(B_prime.get_elements())} elements: {B_prime.get_elements()}")
        if cn(B_prime, alpha):
            return B_prime
    return B_prime

def shrink(B_dataset, alpha):
    i = 0
    max_iterations = len(B_dataset.get_elements()) + 5
    current_iteration = 0
    while i < len(B_dataset.get_elements()):
        if current_iteration > max_iterations:
            logging.error("Forced break for debugging.")
            break
        current_iteration += 1
        element = B_dataset.get_elements()[i]
        logging.info(f"Checking line: {element} with index: {i}")
        cloned_B_dataset = B_dataset.clone()
        logging.debug(f"Removing element: {element}")
        cloned_B_dataset.remove_element(element)
        logging.debug(f"B with {len(cloned_B_dataset.get_elements())} elements = {cloned_B_dataset.get_elements()}")
        if cn(cloned_B_dataset, alpha):
            logging.info(f"SHRINK: CN = TRUE, removing: {element}")
            B_dataset.remove_element(element)
            logging.debug(f"CONTINUE SHRINKING WITH {len(B_dataset.get_elements())} elements : {B_dataset.get_elements()}")
        else:
            i += 1
    logging.info(f"Kernel output with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
    logging.info("KERNEL BLACKBOX FINISHED")
    return B_dataset

def divide_and_conquer(B_dataset, alpha):
    """ Divide-and-conquer shrink method. """
    if B_dataset.size() <= 1:
        logging.info("DC: Dataset size <= 1")
        return B_dataset if cn(B_dataset, alpha) else DataSet()

    logging.info(f"DC splitting Dataset: {B_dataset.get_elements()}")
    B1, B2 = B_dataset.split()

    cn_B1 = cn(B1, alpha)
    cn_B2 = cn(B2, alpha)

    logging.debug(f"DC Check entailment, cn_B1 = {cn_B1}, cn_B2 = {cn_B2}")

    if not cn_B1:
        logging.info("DC: B1 does not entail alpha, calling DC recursively on B2")
        return divide_and_conquer(B2, alpha)

    if not cn_B2:
        logging.info("DC: B2 does not entail alpha, calling DC recursively on B1")
        return divide_and_conquer(B1, alpha)

    logging.info("DC: Both halves entail alpha, merging and shrinking recursively")
    combined_result = B1.combine(B2)
    return divide_and_conquer(combined_result, alpha)

def cn(B_dataset, alpha):
    temp_file = "tmp/temp_dimacs.cnf"
    B_copy = B_dataset.clone()
    B_copy.add_element("!"+alpha)
    B_copy.to_file(temp_file)
    converter = CNFConverter(verbose=False)
    converter.convert_to_cnf(temp_file, temp_file)
    result = subprocess.run(['minisat', temp_file], capture_output=True, text=True)
    output = result.stdout
    last_line = output.splitlines()[-1]
    if "UNSAT" in last_line:
        logging.debug(f"MiniSat result: UNSAT. Therefore, {alpha} is in Cn({B_dataset.get_elements()})")
        return True
    elif "SAT" in last_line:
        logging.debug(f"MiniSat result: SAT. Therefore, {alpha} is not in Cn({B_dataset.get_elements()})")
        return False
    else:
        logging.debug("MiniSat output was unexpected.")
        return None
