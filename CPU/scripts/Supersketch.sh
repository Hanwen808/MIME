#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling Supersketch with $optimize_flag optimization flag..."
g++ ../Sources/MurmurHash3.cpp ../Sources/Supersketch.cpp ../Supersketch_main.cpp -o SS -std=c++17 -I ../C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running Supersketch..."
    ./SS
else
    echo "Compilation failed. Exiting."
    exit 1
fi
