#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling vHLL with $optimize_flag optimization flag..."
g++ ./Sources/MurmurHash3.cpp ./Sources/vHLL.cpp ./vHLL_main.cpp -o vHLL -std=c++17 -I ./C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running vHLL..."
    ./vHLL
else
    echo "Compilation failed. Exiting."
    exit 1
fi