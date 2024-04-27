import logging
import subprocess
from .kernelstrategy import KernelStrategy
from src.parse import CNFConverter
from src.structs.dataset import DataSet

# Configure logging to file
logging.basicConfig(filename='log/remainder_operations.log', # Log file name
                    filemode='w', # Overwrite the log file on each run
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class ShrinkExpand(KernelStrategy):
    def __init__(self, window_size=1, divide_and_conquer=False):  
        # Default to the basic expand-shrink method with window_size = 1 and without Divide_and_conquer
        self.window_size = window_size
        self.div_conq = divide_and_conquer  # Set to FALSE PER DEFAULT UNTIL STRATEGY IMPLEMENTED
    
    def find_kernel(self, dataset, alpha):
        # Make a clone of the dataset to ensure the original is not altered
        dataset_clone = dataset.clone()  # Ensure your dataset object supports cloning
        if self.cn(dataset_clone, alpha):
            remainder = self.find_remainder(dataset_clone, alpha)
            logging.info(f"Found remainder {len(remainder.get_elements())} elements: {remainder.get_elements()}")
            
            # Compute kernel as the difference between original dataset elements and remainder
            original_elements = set(dataset.get_elements())  # Use set for efficient lookup
            remainder_elements = set(remainder.get_elements())
            if original_elements == remainder_elements:
                logging.info(f"No kernel found, remainder = dataset")
                return None
            else:
                kernel_elements = original_elements - remainder_elements
                kernel = DataSet(elements=list(kernel_elements))  # Create a new dataset from the kernel elements

                logging.info(f"Kernel found with {len(kernel.get_elements())} elements: {kernel.get_elements()}")
                return kernel
        else:
            logging.debug(f"Dataset does not entail {alpha}, remainder = {dataset}, kernel = empty")
            return None

    def find_remainder(self, dataset, alpha):
        remainder_dataset = self.shrink(dataset, alpha)
        logging.info(f"After shrink: {remainder_dataset.get_elements()} elements")
        return remainder_dataset

    def shrink(self, B_dataset, alpha):
        """ Shrinks the dataset using a sliding window until alpha is no longer a consequence. """
        # This is the core function for finding the kernel using either a normal approach or divide and conquer
        i = 0
        removed_elements = DataSet()
        while i < len(B_dataset.get_elements()):
            B_prime = B_dataset.clone()
            element = B_prime.get_elements()[i]
            logging.info(f"Checking and removing line: {element} with index: {i}")  # Info about current element and index
            B_prime.remove_element(element)
            logging.debug(f"B_prime with {len(B_prime.get_elements())} elements = {B_prime.get_elements()}")  # Debug log for current dataset state

            # Check if alpha in Cn(B - {beta}, alpha)
            if self.cn(B_prime, alpha):
                removed_elements.add_element(element)
                B_dataset.remove_element(element)
                logging.info(f"SHRINK: CN = {self.cn(B_prime, alpha)}, removing: {element}")  # Info log for dataset shrink action
            else:
                # Increment i only if the element was not removed
                i += 1
                logging.info(f"Remainder output with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")  # Logs the final kernel output
                return self.expand(B_dataset, removed_elements, alpha)

    def expand(self, B_dataset, removed_elements, alpha):
        """ Expands the dataset to ensure maximality while alpha is not entailed. """
        for element in removed_elements.get_elements():
            logging.debug(f"Checking element {element} of {len(removed_elements.get_elements())} removed elements = {removed_elements.get_elements()}")
            B_dataset.add_element(element)
            if self.cn(B_dataset, alpha):
                B_dataset.remove_element(element)  # Remove it if it causes entailment
        
        logging.debug(f"FINAL REMAINDER WITH {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
        return B_dataset

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
        B_copy.add_element("!("+alpha+")")
        logging.debug(f"Checking with B_copy = {B_copy.get_elements()}")

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