import logging
import subprocess
from src.parse import CNFConverter
from src.structs.dataset import DataSet

# Configure logging to file
logging.basicConfig(
    filename='log/kernel_operations.log',  # Log file name
    filemode='w',  # Overwrite the log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',  # Fix typo here
    level=logging.CRITICAL
)

class KernelAndRemainderFinder:
    def __init__(self, window_size=1, divide_and_conquer=False):
        self.window_size = window_size
        self.div_conq = divide_and_conquer

    def find_kernel(self, dataset, alpha):
        if self.cn(dataset, alpha):
            logging.debug(f"Finding kernel for {len(dataset.get_elements())} elements of dataset = {dataset.get_elements()}")
            expanded_dataset = self.expand(dataset, alpha)
            if expanded_dataset:
                return self.shrink(expanded_dataset, alpha)
            return expanded_dataset  # Return the dataset even if empty
        else:
            logging.debug(f"Dataset does not entail {alpha}, kernel = empty")
            return None

    def find_remainder(self, dataset, alpha):
        dataset_clone = dataset.clone()
        if self.cn(dataset_clone, alpha):
            shrunk_dataset = self.shrink(dataset_clone, alpha)
            logging.info(f"Found remainder {len(shrunk_dataset.get_elements())} elements: {shrunk_dataset.get_elements()}")
            return shrunk_dataset
        else:
            logging.debug(f"Dataset does not entail {alpha}, remainder = {dataset.get_elements()}, kernel = empty")
            return None

    def expand(self, B_dataset, alpha):
        elements = B_dataset.get_elements()
        logging.info(f"{len(elements)} ELEMENTS: {elements}")
        B_prime = DataSet()

        counter = 0
        for start in range(0, len(elements), self.window_size):
            counter += 1
            if counter > len(elements) + 5:
                logging.warning("BREAK, MAX ITERATION, RETURNING NONE.")
                return None

            window_end = min(start + self.window_size, len(elements))
            window_elements = elements[start:window_end]
            for element in window_elements:
                B_prime.add_element(element)

            logging.debug(f"B_PRIME with {len(B_prime.get_elements())} elements: {B_prime.get_elements()}")

            if self.cn(B_prime, alpha):
                if self.div_conq:
                    return self.divide_and_conquer(B_prime, alpha)
                else:
                    return B_prime
        return B_prime  # Return even if expansion was not possible

    def shrink(self, B_dataset, alpha):
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

            if self.cn(cloned_B_dataset, alpha):
                logging.info(f"SHRINK: CN = TRUE, removing: {element}")
                B_dataset.remove_element(element)
                logging.debug(f"CONTINUE SHRINKING WITH {len(B_dataset.get_elements())} elements : {B_dataset.get_elements()}")
            else:
                i += 1

        logging.info(f"Kernel output with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
        logging.info("KERNEL BLACKBOX FINISHED")
        return B_dataset

    def expand_from_shrink(self, B_dataset, removed_elements, alpha):
        for element in list(reversed(removed_elements.get_elements())):
            B_dataset.add_element_at_start(element)
            logging.debug(f"EXPAND: Checking element {element} with B = {B_dataset.get_elements()}")
            if self.cn(B_dataset, alpha):
                B_dataset.remove_element(element)
                logging.debug(f"EXPAND: CN = TRUE, removing element {element} with B = {B_dataset.get_elements()}")

        logging.debug(f"FINAL REMAINDER WITH {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
        return B_dataset

    def divide_and_conquer(self, B_dataset, alpha):
        if B_dataset.size() <= 1:
            logging.info("DC: Datasetsize <= 1")
            return B_dataset if self.cn(B_dataset, alpha) else DataSet()

        logging.info(f"DC splitting Dataset: {B_dataset.get_elements()}")
        B1, B2 = B_dataset.split()

        cn_B1 = self.cn(B1, alpha)
        cn_B2 = self.cn(B2, alpha)
        logging.debug(f"DC Check entailment, cn_B1 = {cn_B1}, cn_B2 = {cn_B2}")

        if not cn_B1 and not cn_B2:
            logging.info("Neither half entails alpha, passing halves to shrink.")
            return self.shrink(B_dataset, alpha)

        if cn_B1:
            logging.info(f"Recursively calling DC for B1 = {B1.get_elements()}")
            return self.divide_and_conquer(B1, alpha)
        if cn_B2:
            logging.info(f"Recursively calling DC for B2 = {B2.get_elements()}")
            return self.divide_and_conquer(B2, alpha)

        return DataSet()

    def cn(self, B_dataset, alpha):
        temp_file = "tmp/temp_dimacs.cnf"

        B_copy = B_dataset.clone()
        B_copy.add_element("!(" + alpha + ")")

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
