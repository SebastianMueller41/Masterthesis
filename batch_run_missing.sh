#!/bin/bash

# Set CSV file path (modify if needed)
csv_file="missing_combinatoins_ARG.csv"

# Check if CSV file exists
if [ ! -f "$csv_file" ]; then
  echo "Error: CSV file '$csv_file' not found!"
  exit 1
fi

# Loop through each line in the CSV file
while IFS=, read -r dataset div_conq sw_size strategy_param dataset_length; do
  # Skip header row (if present)
  if [[ $dataset == "dataset" ]]; then
    continue
  fi

  # Execute main.py with the parameters from the CSV line and alpha
  python main.py "$dataset" $div_conq $sw_size $strategy_param --alpha 'arg_0&&!arg_0' --log-db &> /dev/null

  # Print a message indicating completion of the current run
  echo "Finished running with: dataset=$dataset, div_conq=$div_conq, sw_size=$sw_size, strategy_param=$strategy_param, alpha='arg_0&&!arg_0'"
done < "$csv_file"

echo "All runs completed!"
