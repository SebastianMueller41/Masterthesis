import logging
from .kernelstrategy import KernelStrategy
from src.structs.dataset import DataSet
from src.kernels.kernel_utils import cn  # Import the cn function

class ShrinkExpand(KernelStrategy):
    def __init__(self, window_size=1, divide_and_conquer=False):  
        # Default to the basic expand-shrink method with window_size = 1 and without Divide_and_conquer
        self.window_size = window_size
        self.div_conq = divide_and_conquer  # Set to FALSE PER DEFAULT UNTIL STRATEGY IMPLEMENTED
    
    def find_kernel(self, dataset, alpha):
        # Make a clone of the dataset to ensure the original is not altered
        dataset_clone = dataset.clone()  # Ensure your dataset object supports cloning
        if cn(dataset_clone, alpha):  # Use the imported cn function
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
            logging.debug(f"Dataset does not entail {alpha}, remainder = {dataset.get_elements()}, kernel = empty")
            return None

    def find_remainder(self, dataset, alpha):
        remainder_dataset, removed_elements = self.shrink(dataset, alpha)
        logging.info(f"After shrink: {remainder_dataset.get_elements()}")
        if self.div_conq:
            return self.divide_and_conquer(remainder_dataset, removed_elements, alpha)
        else:
            return self.expand(remainder_dataset, removed_elements, alpha)

    def shrink(self, B_dataset, alpha):
        """ Shrinks the dataset using a sliding window until alpha is no longer a consequence. """
        removed_elements = DataSet()
        elements = B_dataset.get_elements()

        # Process the dataset in windows
        for start in range(0, len(elements), self.window_size):
            window_elements = elements[start:start + self.window_size]
            B_prime = B_dataset.clone()
            for element in window_elements:
                B_prime.remove_element(element)
            logging.debug(f"Checking and removing elements: {window_elements}, B_prime now with {len(B_prime.get_elements())} elements = {B_prime.get_elements()}")

            if cn(B_prime, alpha):  # Use the imported cn function
                logging.info(f"SHRINK: CN = TRUE for window elements {window_elements}, B_dataset = {B_prime.get_elements()}, removed elements: {removed_elements.get_elements()}")
                B_dataset = B_prime
                removed_elements.add_element(element)
            else:
                logging.info(f"FINISHED SHRINK, CN = FALSE for window elements {window_elements}, Remainder output with {len(B_prime.get_elements())} elements: {B_prime.get_elements()}, removed elements: {removed_elements.get_elements()}")
                return B_dataset, removed_elements

        logging.info(f"Remainder after sliding window shrink with {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
        return B_dataset, removed_elements

    def expand(self, B_dataset, removed_elements, alpha):
        """ Expands the dataset to ensure maximality while alpha is not entailed. """
        logging.info(f"Starting expanding B {B_dataset.get_elements()} with removed elements: {removed_elements.get_elements()}")
        for element in removed_elements.get_elements():
            logging.debug(f"EXPAND: Checking element {element} with B = {B_dataset.get_elements()}")
            if not cn(B_dataset, alpha):  # Use the imported cn function
                B_dataset.add_element(element)
                logging.debug(f"EXPAND: CN = TRUE, removing element {element} with B = {B_dataset.get_elements()}")
        
        logging.debug(f"FINAL REMAINDER WITH {len(B_dataset.get_elements())} elements: {B_dataset.get_elements()}")
        return B_dataset

    def divide_and_conquer(self, B_dataset, removed_elements, alpha):
        """ Divide-and-conquer expansion method. """
        if removed_elements.size() <= 1:
            return self.expand(B_dataset, removed_elements, alpha)

        logging.info(f"DC_EXPAND: Splitting removed elements: {removed_elements.get_elements()}")
        left_removed, right_removed = removed_elements.split()

        left_expanded = B_dataset.combine(left_removed)
        cn_left = cn(left_expanded, alpha)
        right_expanded = B_dataset.combine(right_removed)
        cn_right = cn(right_expanded, alpha)

        logging.info(f"DC_EXPAND: Left half: {left_removed.get_elements()}, Right half: {right_removed.get_elements()}")

        if not cn_left:
            B_dataset = left_expanded
            removed_elements = right_removed
            logging.info(f"D&C: Left halve added to B, call D&C again with right halve!")
            self.divide_and_conquer(B_dataset, removed_elements, alpha)
        else:
            if not cn_right:
                B_dataset = right_expanded
                removed_elements = left_removed
                logging.info(f"D&C: Right halve added to B, call D&C again with left halve!")
                self.divide_and_conquer(B_dataset, removed_elements, alpha)
            else:
                B_dataset = B_dataset.combine(self.divide_and_conquer(B_dataset, left_removed, alpha))
                return self.divide_and_conquer(B_dataset, right_removed, alpha)