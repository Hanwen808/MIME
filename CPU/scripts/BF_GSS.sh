#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling BF+GSS with $optimize_flag optimization flag..."
g++ ../Sources/bitmap.cpp ../Sources/MurmurHash3.cpp ../Sources/BF_GSS.cpp ../Sources/GSS.cpp ../BF_GSS_main.cpp -o BF_GSS -std=c++17 -I ../C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running BF+GSS..."
    ./BF_GSS
else
    echo "Compilation failed. Exiting."
    exit 1
fi