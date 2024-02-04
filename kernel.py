"""
This module defines a set of functions to apply the expand-shrink algorithm on a dataset. 
The main functionality is to find a kernel for a dataset with respect to a given parameter alpha.
It leverages a SAT solver (MiniSat) to check for the consequences of the dataset and utilizes 
a branch and bound strategy for kernel extraction.

The module contains the following key functions:
- expand_shrink: Applies the expand-shrink algorithm to find a kernel.
- kernel_black_box: Identifies one element of the kernel with respect to alpha.
- Cn: Checks whether alpha is a consequence of the dataset using MiniSat.
"""

import subprocess
from dataset import DataSet

def expand_shrink(B_dataset, alpha):
    """
    Apply the expand-shrink algorithm to find a kernel for a given dataset.
    
    Iterates over the elements of B_dataset, and for each element, checks if
    the current set entails alpha. If it does, it calls the kernel_black_box
    function and returns its result.

    Args:
        B_dataset (DataSet): The dataset containing the elements to be processed.
        alpha (str): The element to be checked against the dataset.

    Returns:
        list: The kernel found, if any.
    """
    B_prime = DataSet()
    # Iterate over B and add each line to B_prime
    for line in B_dataset.get_elements():
        B_prime.add_element(line)
        print("Actual line: " + line)
        print("B_prime: " + str(B_prime.get_elements()))
        # Check if alpha is entailed by B_prime
        if Cn(B_prime, alpha):
            print("CALLING SHRINKING WITH B_prime: " + str(B_prime.get_elements()))
            return kernel_black_box(B_prime, alpha)

def kernel_black_box(B_dataset, alpha, output_file_path="Temp/found_kernels"):
    """
    Find one element of the kernel B with respect to alpha and save it to a file.
    
    Iterates over the elements of B_dataset, clones the dataset, and removes an element.
    It then checks if alpha is in the consequences of the modified dataset. If not,
    the element is removed from the original dataset.

    Args:
        B_dataset (DataSet): The dataset to be processed.
        alpha (str): The element to be checked against the dataset.
        output_file_path (str): The file path where the kernel will be saved.

    Returns:
        DataSet: The dataset after processing with kernel_black_box.
    """
    i = 0
    # Iterate over elements of B, clone B and remove element
    while i < len(B_dataset.get_elements()):
        element = B_dataset.get_elements()[i]
        print("Checking line: " + element + " with index: " + str(i))
        cloned_B_dataset = B_dataset.clone()
        print("Removing element: " + element)
        cloned_B_dataset.remove_element(element)
        print("B = " + str(cloned_B_dataset.get_elements()))
        # Check if alpha in Cn(B - {beta}, alpha)
        if Cn(cloned_B_dataset, alpha):
            print("SHRINK: " + alpha + " in CN, removing: " + element)
            B_dataset.remove_element(element)
            print("CONTINUE SHRINKING WITH : " + str(B_dataset.get_elements()))
            # Do not increment i, since we want to check the new element at the same index after removal
        else:
            # Increment i only if the element was not removed
            i += 1


    print("Kernel output: " + str(B_dataset.get_elements()))
    print("KERNEL BLACKBOX FINISHED")
    return B_dataset

def Cn(B_dataset, alpha):
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
    temp_file="Temp/temp_dimacs.cnf"

    # Clone B and add !alpha to check for entailment
    B_copy = B_dataset.clone()
    B_copy.add_element("!"+alpha)
    print("Checking Cn() with B: "+ str(B_copy.get_elements()))

    # Call parse.py to transform B_copy into CNF
    B_copy.to_file(temp_file)
    subprocess.run(['python', 'parse.py', temp_file, temp_file])

    # Call miniSat and interpret the output
    result = subprocess.run(['minisat', temp_file], capture_output=True, text=True)
    output = result.stdout

    # Extract the last line to check for the "SAT" or "UNSAT" result
    last_line = output.splitlines()[-1]

    # Process the output
    if "UNSAT" in last_line:
        print(f"MiniSat result: UNSAT. Therefore, {alpha} is in Cn({B_dataset.get_elements()})")
        return True
    elif "SAT" in last_line:
        print(f"MiniSat result: SAT. Therefore, {alpha} is not in Cn({B_dataset.get_elements()})")
        return False
    else:
        print("MiniSat output was unexpected.")
        return None
