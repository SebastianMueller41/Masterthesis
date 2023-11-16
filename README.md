# Masterthesis

To get started, please make sure that you have installed lark.
If not please install it as follows:

pip3 install lark

The code can use two different solvers.

To use the minisat solver, ensure that the minisat solver is installed.
Please follow the following instructions to install the minisat solver.

Linux (Debian/Ubuntu):
sudo apt-get install minisat

macOS (using Homebrew):
brew install minisat

From Source:
git clone https://github.com/niklasso/minisat.git
cd minisat
make config prefix=/your/preferred/directory
make install

To use the maxsat solver please follow the instructions to install it as follows.

First install gmp.

For Linux:
sudo apt-get install libgmp-dev

For macOS:
brew install gmp

For Windows:
If you're using Windows, you can download precompiled binaries or source code from the GMP website (https://gmplib.org/). 
Installing from source will require additional steps, including configuration and compilation.

Please note that it might be necessary to change the CFLAG in the Makefile of the open-wbo solver.

After the installation the program can be used with minisat or maxsat as arguments.

To run the program with the minisat solver use the following code.

python3 main.py minisat Dataset_a/sig3_5_15/srs_0.txt         