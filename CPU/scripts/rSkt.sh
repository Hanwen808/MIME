#!/bin/bash

# options
optimize_flag="-O3"

# compile
echo "Compiling rSkt with $optimize_flag optimization flag..."
g++ ../Sources/MurmurHash3.cpp ../Sources/rSkt.cpp ../rSkt_main.cpp -o rSkt -std=c++17 -I ../C++ $optimize_flag

if [ $? -eq 0 ]; then
    echo "Compilation successful. Running rSkt..."
    ./rSkt
else
    echo "Compilation failed. Exiting."
    exit 1
fi