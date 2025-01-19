#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling MIME with $optimize_flag optimization flag..."
g++ ./Sources/bitmap.cpp ./Sources/MurmurHash3.cpp ./Sources/MIME.cpp ./MIME_main.cpp -o MIME -std=c++17 -I ./C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running MIME..."
    ./MIME
else
    echo "Compilation failed. Exiting."
    exit 1
fi