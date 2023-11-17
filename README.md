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
````
**MaxSAT Solver**
To use the MaxSAT solver, you'll need to install 'gmp' (GNU Multiple Precision Arithmetic Library) first.

Linux:
```bash
sudo apt-get install libgmp-dev
```
For macOS:
```bash
brew install gmp
```
Windows:
For Windows users, you can download precompiled binaries or source code from the GMP website (https://gmplib.org/).' Installing from source will require additional steps, including configuration and compilation.

Please note that you may need to adjust the CFLAGS in the Makefile of the Open-WBO solver if necessary.

Running the Program
After the installation, you can use the program with either the Minisat or MaxSAT solver as arguments.

To run the program with the Minisat solver, use the following command:

```bash
python3 main.py minisat Dataset_a/sig3_5_15/srs_0.txt         
python3 main.py maxsat Dataset_a/sig3_5_15/srs_0.txt
```
To use the program with different Datasets, please change the path/to/file accordingly.

Feel free to reach out if you have any questions or need further assistance!
