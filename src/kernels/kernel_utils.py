import logging
import subprocess
import sys
from src.CNFconverter.parse import CNFConverter
from src.structs.dataset import DataSet

def expand(B_dataset, alpha, window_size=1):
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

def expand_divide_and_conquer(B_dataset, alpha, removed_elements=None):
    """ Divide-and-conquer expansion method. """
    if removed_elements is None:
        removed_elements = B_dataset.clone()  # Initially, consider all elements for removal

    if removed_elements.size() <= 1:
        return expand(B_dataset, alpha)

    logging.info(f"DC_EXPAND: Splitting removed elements: {removed_elements.get_elements()}")
    left_removed, right_removed = removed_elements.split()

    left_expanded = B_dataset.clone().combine(left_removed)
    cn_left = cn(left_expanded, alpha)
    right_expanded = B_dataset.clone().combine(right_removed)
    cn_right = cn(right_expanded, alpha)

    logging.info(f"DC_EXPAND: Left half: {left_removed.get_elements()} entails alpha: {cn_left}, Right half: {right_removed.get_elements()} entails alpha: {cn_right}")

    if cn_left:
        logging.info(f"D&C: Left half added to B, call D&C again with right half!")
        return expand_divide_and_conquer(left_expanded, alpha, right_removed)
    elif cn_right:
        logging.info(f"D&C: Right half added to B, call D&C again with left half!")
        return expand_divide_and_conquer(right_expanded, alpha, left_removed)
    else:
        combined_result = expand_divide_and_conquer(B_dataset, alpha, left_removed)
        combined_result = combined_result.combine(expand_divide_and_conquer(B_dataset, alpha, right_removed))
        return combined_result
    
def expand_divide_and_conquer(B_dataset, alpha):
    """Divide-and-conquer expansion method"""
    if B_dataset.size() <= 1:
        return B_dataset
    else:
        logging.info(f"DC_EXPAND: Splitting B: {B_dataset.get_elements()}")
        B1, B2 = B_dataset.split()
        cn_B1 = cn(B1, alpha)
        cn_B2 = cn(B2, alpha)

        logging.info(f"DC_EXP: Left half {B1.get_elements()},cn(alpha):{cn_B1} ")
        logging.info(f"DC_EXP: Right half {B2.get_elements()},cn(alpha):{cn_B2}")

        if cn_B1:
            logging.info(f"DC_EXP CALLING DC WITH LEFT HALVE: {B1.get_elements()}")
            return expand_divide_and_conquer(B1,alpha)
        else:
            if cn_B2:
                logging.info(f"DC_EXP CALLING DC WITH RIGHT HALVE: {B2.get_elements()}")
                return expand_divide_and_conquer(B2, alpha)
            else:
                B_dataset = B1.combine(B2)
                logging.info(f"B1 and B2 does not entail alpha, returning B: {B_dataset.get_elements()}")
                return expand(B_dataset, alpha)

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

def shrink_sliding_window(B_dataset, alpha, window_size):
    """ Shrinks the dataset using a sliding window until alpha is no longer a consequence. """
    removed_elements = DataSet()
    elements = B_dataset.get_elements()
    start = 0

    # Process the dataset in windows
    while start < len(elements):
        window_elements = elements[start:start + window_size]
        B_prime = B_dataset.clone()
        for element in window_elements:
            B_prime.remove_element(element)
        logging.debug(f"Checking and removing elements: {window_elements}, B_prime now with {len(B_prime.get_elements())} elements = {B_prime.get_elements()}")

        if not cn(B_prime, alpha):  # Use the imported cn function
            logging.info(f"SHRINK: CN = FALSE for window elements {window_elements}, B_dataset = {B_prime.get_elements()}, removed elements: {removed_elements.get_elements()}")
            start += window_size  # Step size is window_size
        else:
            logging.info(f"CN = TRUE for window elements {window_elements}. Deleting these elements.")
            B_dataset = B_prime
            for element in window_elements:
                removed_elements.add_element(element)
            start += 1  # Step size is 1

    logging.info(f"Remainder after sliding window shrink with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
    return shrink(B_dataset, alpha)

def shrink_divide_and_conquer(B_dataset, alpha):
    """ Divide-and-conquer shrink method. """
    if B_dataset.size() <= 1:
        logging.info("DC: Dataset size <= 1")
        return B_dataset

    logging.info(f"DC splitting Dataset: {B_dataset.get_elements()}")
    B1, B2 = B_dataset.split()

    cn_B1 = cn(B1, alpha)
    cn_B2 = cn(B2, alpha)

    logging.debug(f"DC Check entailment, cn_B1 = {cn_B1}, cn_B2 = {cn_B2}")

    if cn_B1:
        logging.info("DC: B1 does not entail alpha, calling DC recursively on B2")
        return shrink_divide_and_conquer(B1, alpha)

    if cn_B2:
        logging.info("DC: B2 does not entail alpha, calling DC recursively on B1")
        return shrink_divide_and_conquer(B2, alpha)

    combined_result = B1.combine(B2)
    logging.info(f"DC: Both halves entail alpha, merging and shrinking with {combined_result.get_elements()}")
    return shrink(combined_result, alpha)

def cn(B_dataset, alpha):
    temp_file = "tmp/temp_dimacs.cnf"
    B_copy = B_dataset.clone()
    B_copy.add_element("!("+alpha+")")
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
        print("MiniSat output was unexpected.")
        logging.debug("MiniSat output was unexpected.")
        sys.exit(1)
