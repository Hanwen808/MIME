FPGA implementation of MIME
============

Core File Description
--------------------
*  `update_B.v`: the implementation of on-chip filter.
*  `update.v`: the implementation of MIME (top-level module).
*  `PCIE_test_codes/`: the core pcie function codes.
*  `update_fcmp_32ns_32ns_1_2_no_dsp_1.v`: comparation between two uint32_t in `./Synthesis_C/murmurhash.cpp`.
*  `update_fdiv_32ns_32ns_32_7_no_dsp_1.v`: division algorithm between two float in `./Synthesis_C/murmurhash.cpp`.
*  `update_fmul_32ns_32ns_32_2_max_dsp_1.v`: multiplicity algorithm between two uint32_t in `./Synthesis_C/murmurhash.cpp`.

Experimental setup
--------------------
* compile: Vivado 2020
* language: Verilog
