# FPGA Implementation

This is the implementation for MIME.

## Platform

This implementation is completed on a NetFPGA-1G-CML FPGA development board with 4.5 MB SRAM and four Ethernet interfaces capable of negotiating up to 1 GB/s connections. The development board is connected to a workstation (with a Ryzen7 1700 @3.0GHZ CPU and 64 GB RAM) through PCIe Gen2 X4 lanes. 

We provide C++ codes in CPP_simualations for hardware implementation here, which can be directly synthesized into Verilog codes using Vivado HLS.
