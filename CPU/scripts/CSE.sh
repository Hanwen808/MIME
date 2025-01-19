#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling CSE with $optimize_flag optimization flag..."
g++ ./Sources/bitmap.cpp ./Sources/MurmurHash3.cpp ./Sources/CSE.cpp ./CSE_main.cpp -o CSE -std=c++17 -I ./C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running CSE..."
    ./CSE
else
    echo "Compilation failed. Exiting."
    exit 1
fi