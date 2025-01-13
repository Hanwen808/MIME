On-Chip/Off-Chip PCIe Communication Functionality
============

File Description
--------------------
*  `gmii_2_rgmii.v`: The top-level module for `rgmii_rx1.v` and `rgmii_tx1.v`.
*  `rgmii_rx1.v`: The implementation for the conversion of DDR data from an RGMII interface to SDR data.
*  `rgmii_tx1.v`: Converting single-edge 8-bit data into double-edge 4-bit data.
*  `udp_rx.v`: parsing packets using the UDP protocol to extract packet fields and construct stream items.
*  `udp_top.v`: the top-level module for `udp_rx.v`.

Experimental setup
--------------------
* compile: Vivado 2020
* language: Verilog
