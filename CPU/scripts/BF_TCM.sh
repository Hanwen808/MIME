#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling BF+TCM with $optimize_flag optimization flag..."
g++ ./Sources/bitmap.cpp ./Sources/MurmurHash3.cpp ./Sources/BF_TCM.cpp ./Sources/TCM.cpp ./BF_TCM_main.cpp -o BF_TCM -std=c++17 -I ./C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running BF+TCM..."
    ./BF_TCM
else
    echo "Compilation failed. Exiting."
    exit 1
fi