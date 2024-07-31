
# Masterthesis

This project involves a Python-based kernelization process using various search strategies and pruning techniques. Follow the instructions below to set up your environment and execute the script.

## Setup

### Virtual Environment

It is highly recommended to create a virtual environment to manage your project's dependencies.

```bash
python3 -m venv pyenv
source pyenv/bin/activate  # Unix-like systems
pyenv\Scripts\activate     # Windows Command Prompt
```

### Install Dependencies

Install all required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### External Solvers

The code requires the `minisat` solver. Ensure it is installed on your system.

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install minisat
```

**macOS (using Homebrew):**

```bash
brew install minisat
```

**Building from Source:**

```bash
git clone https://github.com/niklasso/minisat.git
cd minisat
make config prefix=/your/preferred/directory
make install
```

Ensure the `minisat` binary is in your system's PATH so it can be invoked from the Python script.

## Running the Script

The main script requires several arguments and options. Below are the descriptions of each parameter and how to use them.

### Parameters

- `filepath` (str): Path to the dataset file.
- `--vp` (int, required): Value parameter for value assignment used for Branch-and-Bound.
  - `1`: Cardinality
  - `2`: Random Values
  - `3`: Inconsistency Values
- `--ss` or `--search-strategy` (str, required): Search strategy to use. Choices are `BFS`, `DFS`, `HYS`, `PBS`.
- `--alpha` (str, required): A string value to be used as alpha.
- `--pruner` (str, default='NONE'): Pruning/Boundary strategy to use. Choices are `UPPER`, `LOWER`, `BEST`, `NONE`.

### Expand Options

- `--expand-div-conq`: Activate the divide and conquer technique for expand.
- `--expand-sw-size` (int, default=1): Window size for the sliding-window technique during expand.

### Shrink Options

- `--shrink-div-conq`: Activate the divide and conquer technique for shrink.
- `--shrink-sw-size` (int, default=1): Window size for the sliding-window technique during shrink.

### Other Options

- `-res-db`: Save results to the database.
- `-no-log`: Disable logging.
- `-path-db`: Indicate that the dataset should be called from the database.

## Examples

To run the script with a specific dataset and strategy, use the following command:

```bash
python main.py path/to/dataset/file.txt --vp 1 --ss BFS --alpha "your_alpha_value"
```

Replace `path/to/dataset/file.txt` with the actual path to your dataset and adjust the parameters (`--vp`, `--ss`, `--alpha`) as needed.

### Example Command

```bash
python main.py Dataset_a/sig3_5_15/srs_0.txt --vp 1 --ss BFS --alpha "alpha_value"
```

## Support

If you have any questions or need further assistance, feel free to reach out!
