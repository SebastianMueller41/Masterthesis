"""
This module provides functions to calculate the inconsistency weights of datasets counting the instances that are consistent for evaluation
"""


import os
import csv
from collections import defaultdict

# Directory containing the .pl files
directory = 'data/ARG/'

# CSV file listing filenames to include
include_file = os.path.join(directory, 'ARG.csv')

def categorize_count(count):
    """
    Categorize counts into 5-step intervals.

    Args:
        count (int): The count to be categorized.

    Returns:
        int: The count categorized into 5-step intervals.
    """
    return (count // 5) * 5

# Read the filenames to include
include_filenames = set()
if os.path.exists(include_file):
    with open(include_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            include_filenames.add(row[0].strip())

# Debug: Print included filenames
print("Included filenames:")
for filename in include_filenames:
    print(filename)

# List to store the results
results = []

# Dictionary to store category counts
category_counts = defaultdict(int)
signature_category_counts = defaultdict(int)

# Dictionary to store detailed data for each signature size category
detailed_categories = defaultdict(list)

# Loop through the specified .pl files in the directory
for full_filepath in include_filenames:
    print(f"Processing file: {full_filepath}")
    if os.path.exists(full_filepath) and full_filepath.endswith('.pl'):
        with open(full_filepath, 'r') as file:
            # Read all lines
            lines = file.readlines()
            if not lines:
                print(f"No lines read from {full_filepath}")
            else:
                # Strip whitespace and newlines from each line
                stripped_lines = [line.strip() for line in lines if line.strip()]
                # Count the number of lines in the file
                line_count = len(stripped_lines)
                print(f"Number of lines in {full_filepath}: {line_count}")
                # Count the number of unique elements (signature size)
                signature_size = len(set(stripped_lines))
                print(f"Signature size of {full_filepath}: {signature_size}")
                # Categorize the number of formulas and signature size
                formula_category = categorize_count(line_count)
                signature_category = categorize_count(signature_size)
                # Append the result to the list
                results.append([full_filepath, signature_category, line_count, formula_category])
                # Update category counts
                category_counts[formula_category] += 1
                signature_category_counts[signature_category] += 1
                # Store detailed data for each signature size category
                detailed_categories[signature_category].append(line_count)

# Debug: Print results
print("\nResults:")
for result in results:
    print(result)

# Print the summary for formula categories
print("\nSummary for formula categories:")
for category, count in sorted(category_counts.items()):
    print(f"Formula Category {category}: {count} Knowledge Bases")

# Print the summary for signature size categories
print("\nSummary for signature size categories:")
for category, count in sorted(signature_category_counts.items()):
    print(f"Signature Size Category {category}: {count} Knowledge Bases")

# Print the detailed categorization for each signature size category
print("\nDetailed categorization for each signature size category:")
for category, line_counts in sorted(detailed_categories.items()):
    min_count = min(line_counts)
    max_count = max(line_counts)
    knowledge_base_count = len(line_counts)
    print(f'Signature size {category}: {knowledge_base_count} Knowledge Bases, Formula count range: {min_count} - {max_count}')
