# Masterthesis

This project includes a Python script that requires specific packages and solvers to run. Follow these instructions to set up your environment and execute the script.

## Setup

### Virtual Environment

First, create a virtual environment to manage your project's dependencies. This step is optional but highly recommended.

```bash
python3 -m venv pyenv
source pyenv/bin/activate  # Unix-like systems
pyenv\Scripts\activate     # Windows Command Prompt
```

### Install Dependencies

Install all required Python packages in 'requirements.txt'.

```bash
pip install -r requirements.txt
```

### External solvers

The code supports using the minisat solver. Make sure to install minisat on your system.

Linux (Debian/Ubuntu):

```bash
sudo apt-get install minisat
```

macOS (using Homebrew):

```bash
brew install minisat
```

Building from Source:

```bash
git clone https://github.com/niklasso/minisat.git
cd minisat
make config prefix=/your/preferred/directory
make install
```

Ensure the minisat binary is in your system's PATH so that it can be invoked from the Python script.

## Running the Script

The main script requires two arguments:

file_path: Path to the dataset/knowledgebase file.
strategy_param: Strategy parameter indicating the approach to use.
1: Cardinality
2: Random
3: Inconsistency

## Examples

To run the script with a specific dataset and strategy, use the following command:

```bash
python main.py path/to/dataset/file.txt 1
```

Replace path/to/dataset/file.txt with the actual path to your dataset and adjust the strategy parameter (1, 2, or 3) as needed.

For example:

```bash
python main.py Dataset_a/sig3_5_15/srs_0.txt 1
```

## Support

Feel free to reach out if you have any questions or need further assistance!
