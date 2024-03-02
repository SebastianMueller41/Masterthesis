# Masterthesis

To get started, please make sure that you have installed lark.
If not please install it as follows:

```bash
pip3 install lark
```

**Solvers**

The code supports two different solvers.

**Minisat Solver**

To use the Minisat solver, ensure that the Minisat solver is installed. Follow the instructions based on your operating system:

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

Examples:

```bash
python3 main.py Dataset_a/sig3_5_15/srs_0.txt
python3 main.py Dataset_a/sig3_5_15/srs_0.txt
```

To use the program with different Datasets, please change the path/to/file accordingly.

Feel free to reach out if you have any questions or need further assistance!
