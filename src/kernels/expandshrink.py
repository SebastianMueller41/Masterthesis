import subprocess
from .kernelstrategy import KernelStrategy
from src.parse import CNFConverter
from src.structs.dataset import DataSet

class ExpandShrink(KernelStrategy):
    def __init__(self, window_size=1, divide_and_conquer=False):  # Default to the basic expand-shrink method with window_size = 1 and without Divide_and_conquer
        self.window_size = window_size
        self.divide_and_conquer = False # Set to FALSE PER DEFAULT UNTIL STRATEGY IMPLEMENTED
    
    def find_kernel(self, dataset, alpha):
            return self.expand_shrink(dataset, alpha)
    
    def expand_shrink(self, B_dataset, alpha):
        elements = B_dataset.get_elements()
        #print(f"ELEMENTS: {elements}")
        B_prime = DataSet()

        for start in range(0, len(elements), self.window_size):
            # Calculate the end of the current window, ensuring not to exceed the dataset's bounds
            window_end = min(start + self.window_size, len(elements))

            # Add elements from the current window to B_prime
            window_elements = elements[start:window_end]
            for element in window_elements:
                B_prime.add_element(element)

            #print(f"B_PRIME: {B_prime.get_elements()}")

            # After adding the window to B_prime, check if alpha is entailed
            if self.cn(B_prime, alpha):
                # If alpha is entailed by the current B_prime, refine it to find the kernel
                return self.kernel_black_box(B_prime, alpha)
            
    def kernel_black_box(self, B_dataset, alpha):
        """
        Optionally apply divide and conquer technique or the normal approach to find the kernel.
        
        Args:
            B_dataset (DataSet): The dataset to be processed.
            alpha (str): The element to be checked against the dataset.
            output_file_path (str): The file path where the kernel will be saved.
            use_divide_and_conquer (bool): If True, use the divide and conquer technique; otherwise, use the normal approach.
        
        Returns:
            DataSet: The dataset after processing with kernel_black_box.
        """
        if self.divide_and_conquer:
            # The divide and conquer implementation
            def divide_and_conquer(B_dataset):
                pass #TODO: Implement divide and conquer
            
            return divide_and_conquer(B_dataset)
        else:
            # The normal kernel_black_box implementation
            i = 0
            # Iterate over elements of B, clone B and remove element
            while i < len(B_dataset.get_elements()):
                element = B_dataset.get_elements()[i]
                #print("Checking line: " + element + " with index: " + str(i))
                cloned_B_dataset = B_dataset.clone()
                #print("Removing element: " + element)
                cloned_B_dataset.remove_element(element)
                #print("B = " + str(cloned_B_dataset.get_elements()))
                # Check if alpha in Cn(B - {beta}, alpha)
                if self.cn(cloned_B_dataset, alpha):
                    #print("SHRINK: " + alpha + " in CN, removing: " + element)
                    B_dataset.remove_element(element)
                    #print("CONTINUE SHRINKING WITH : " + str(B_dataset.get_elements()))
                    # Do not increment i, since we want to check the new element at the same index after removal
                else:
                    # Increment i only if the element was not removed
                    i += 1

            #print("Kernel output: " + str(B_dataset.get_elements()))
            #print("KERNEL BLACKBOX FINISHED")
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
        B_copy.add_element("!"+alpha)
        #print("Checking Cn() with B: "+ str(B_copy.get_elements()))

        # Call parse.py to transform B_copy into CNF
        B_copy.to_file(temp_file)
        #subprocess.run(['python3', 'parse.py', temp_file, temp_file])
        converter = CNFConverter(verbose=False)
        converter.convert_to_cnf(temp_file, temp_file)

        # Call miniSat and interpret the output
        result = subprocess.run(['minisat', temp_file], capture_output=True, text=True)
        output = result.stdout

        # Extract the last line to check for the "SAT" or "UNSAT" result
        last_line = output.splitlines()[-1]

        # Process the output
        if "UNSAT" in last_line:
            #print(f"MiniSat result: UNSAT. Therefore, {alpha} is in Cn({B_dataset.get_elements()})")
            return True
        elif "SAT" in last_line:
            #print(f"MiniSat result: SAT. Therefore, {alpha} is not in Cn({B_dataset.get_elements()})")
            return False
        else:
            #print("MiniSat output was unexpected.")
            return None