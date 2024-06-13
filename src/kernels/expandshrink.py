import logging
import subprocess
from .kernelstrategy import KernelStrategy
from src.parse import CNFConverter
from src.structs.dataset import DataSet

# Configure logging to file
logging.basicConfig(filename='log/kernel_operations.log', # Log file name
                    filemode='w', # Overwrite the log file on each run
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.CRITICAL)

class ExpandShrink(KernelStrategy):
    def __init__(self, window_size=1, divide_and_conquer=False):  
        # Default to the basic expand-shrink method with window_size = 1 and without Divide_and_conquer
        self.window_size = window_size
        self.div_conq = divide_and_conquer  # Set to FALSE PER DEFAULT UNTIL STRATEGY IMPLEMENTED
    
    def find_kernel(self, dataset, alpha):
        if self.cn(dataset, alpha):
            # Starts the kernel finding process
            logging.debug(f"Finding kernel for {len(dataset.get_elements())} elements of dataset = {dataset.get_elements()}")
            return self.expand(dataset, alpha)
        else:
            logging.debug(f"Dataset does not entail {alpha}, kernel = empty")
            return None
    
    def expand(self, B_dataset, alpha):
        # This function attempts to expand and then shrink the dataset around the concept 'alpha'
        elements = B_dataset.get_elements()
        logging.info(f"{len(elements)} ELEMENTS: {elements}")  # Shows the elements being processed
        B_prime = DataSet()

        counter = 0

        for start in range(0, len(elements), self.window_size):
            counter += 1
            if counter > len(elements) + 5:
                logging.warning("BREAK, MAX ITERATION, RETURNING NONE.")  # Logs a break in iteration
                return None
            # Calculate the end of the current window, ensuring not to exceed the dataset's bounds
            window_end = min(start + self.window_size, len(elements))

            # Add elements from the current window to B_prime
            window_elements = elements[start:window_end]
            for element in window_elements:
                B_prime.add_element(element)

            logging.debug(f"B_PRIME with {len(B_prime.get_elements())} elements: {B_prime.get_elements()}")  # Logs the elements in B_prime after addition

            # After adding the window to B_prime, check if alpha is entailed
            if self.cn(B_prime, alpha):
                # If alpha is entailed by the current B_prime, refine it to find the kernel
                if self.div_conq:
                    return self.divide_and_conquer(B_prime, alpha)  # Divide and conquer strategy
                else:
                    return self.shrink(B_prime, alpha)  # Regular kernel black box strategy
            
    def shrink(self, B_dataset, alpha):
        # This is the core function for finding the kernel using either a normal approach or divide and conquer
        i = 0
        max_iterations = len(B_dataset.get_elements()) + 5  # Temporary limit for debugging
        current_iteration = 0
        while i < len(B_dataset.get_elements()):
            if current_iteration > max_iterations:
                logging.error("Forced break for debugging.")  # Error logged if max iterations reached
                break
            current_iteration += 1
            element = B_dataset.get_elements()[i]
            logging.info(f"Checking line: {element} with index: {i}")  # Info about current element and index
            cloned_B_dataset = B_dataset.clone()
            logging.debug(f"Removing element: {element}")  # Debug log for element removal
            cloned_B_dataset.remove_element(element)
            logging.debug(f"B with {len(cloned_B_dataset.get_elements())} elements = {cloned_B_dataset.get_elements()}")  # Debug log for current dataset state

            # Check if alpha in Cn(B - {beta}, alpha)
            if self.cn(cloned_B_dataset, alpha):
                logging.info(f"SHRINK: CN = TRUE, removing: {element}")  # Info log for dataset shrink action
                B_dataset.remove_element(element)
                logging.debug(f"CONTINUE SHRINKING WITH {len(B_dataset.get_elements())} elements : {B_dataset.get_elements()}")  # Debug log for continued shrinking
                # Do not increment i, since we want to check the new element at the same index after removal
            else:
                # Increment i only if the element was not removed
                i += 1

        logging.info(f"Kernel output with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")  # Logs the final kernel output
        logging.info("KERNEL BLACKBOX FINISHED")  # Indicates the end of the kernel black box process
        return B_dataset
        
    def divide_and_conquer(self, B_dataset, alpha):
        #print(f"Checking B_dataset: {B_dataset.get_elements()}, cn: {self.cn(B_dataset, alpha)}")
        
        # Base case: If the dataset is too small to split further meaningfully.
        if B_dataset.size() <= 1:
            logging.info("DC: Datasetsize <= 1")
            return B_dataset if self.cn(B_dataset, alpha) else DataSet()

        # Split the dataset into two halves.
        logging.info(f"DC splitting Dataset: {B_dataset.get_elements()}")
        B1, B2 = B_dataset.split()

        # Check entailment for each half.
        cn_B1 = self.cn(B1, alpha)
        cn_B2 = self.cn(B2, alpha)
        logging.debug(f"DC Check entailment, cn_B1 = {cn_B1}, cn_B2 = {cn_B2}")

        # If both halves fail the entailment check, pass them to shrink.
        if not cn_B1 and not cn_B2:
            logging.info("Neither half entails alpha, passing halves to shrink.")
            return self.shrink(B_dataset, alpha)

        # Recursively divide and conquer if any half entails alpha.
        if cn_B1:
            logging.info(f"Recursively calling DC for B1 = {B1.get_elements()}")
            return self.divide_and_conquer(B1, alpha)
        if cn_B2:
            logging.info(f"Recursively calling DC for B2 = {B2.get_elements()}")
            return self.divide_and_conquer(B2, alpha)

        # Fallback, in case an unforeseen condition occurs.
        return DataSet()

    def cn(self, B_dataset, alpha):
        """
        Check if alpha is a consequence of the dataset using MiniSat.
        
        Clones the given dataset, adds the negation of alpha, and transforms it into CNF.
        Then calls MiniSat to solve the CNF. Interprets the output to determine if alpha
        is a consequence of the dataset.

        Args:
            B_dataset (DataSet): The dataset containing elements to check against.
            alpha (str): The element to check.

        Returns:
            bool: True if alpha is a consequence of the dataset, False otherwise.
        """
        temp_file="tmp/temp_dimacs.cnf"

        # Clone B and add !alpha to check for entailment
        B_copy = B_dataset.clone()
        B_copy.add_element("!"+alpha)

        # Call parse.py to transform B_copy into CNF
        B_copy.to_file(temp_file)
        converter = CNFConverter(verbose=False)
        converter.convert_to_cnf(temp_file, temp_file)

        # Call miniSat and interpret the output
        result = subprocess.run(['minisat', temp_file], capture_output=True, text=True)
        output = result.stdout

        # Extract the last line to check for the "SAT" or "UNSAT" result
        last_line = output.splitlines()[-1]

        # Process the output
        if "UNSAT" in last_line:
            logging.debug(f"MiniSat result: UNSAT. Therefore, {alpha} is in Cn({B_dataset.get_elements()})")
            return True
        elif "SAT" in last_line:
            logging.debug(f"MiniSat result: SAT. Therefore, {alpha} is not in Cn({B_dataset.get_elements()})")
            return False
        else:
            logging.debug("MiniSat output was unexpected.")
            return None