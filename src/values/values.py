import random
from src.values.inconsistency import calculate_inconsistency

def assign_fixed_value(dataset, value):
    """
    Assigns the fixed value of 1 to each element in the dataset.

    Args:
        dataset (DataSet): The dataset to modify.
        value (int): The fixed value that will be assigned to each element of the Dataset.
    """
    dataset.element_values = {element: value for element in dataset.elements}

def assign_unique_random_values(dataset):
    """
    Assign a unique random positive integer value to each element in the dataset.
    Ensures no value is assigned twice.

    Args:
        dataset (DataSet): The dataset to modify.
    """
    # Generate a list of integers from 1 up to the number of elements in the dataset
    range_of_values = list(range(1, len(dataset.get_elements()) + 1))
    
    # Shuffle the list to randomize the order of integers
    random.shuffle(range_of_values)
    
    # Assign each element a unique value from the shuffled list
    for i, element in enumerate(dataset.elements):
        dataset.element_values[element] = range_of_values[i]
    
    print(f"Random values: {dataset.get_values()}")

def assign_inconsistency_value(dataset):
    output_file_path = "tmp/dataset.txt"
    dataset.to_file(output_file_path)
    values = calculate_inconsistency(output_file_path)

    for i, element in enumerate(dataset.elements):
        dataset.element_values[element] = values[i]

    with open(output_file_path, "a") as file:
        file.write(f"\nInconsistensy Measures: {dataset.get_values()}")