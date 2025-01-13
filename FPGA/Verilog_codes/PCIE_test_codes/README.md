On-Chip/Off-Chip PCIe Communication Functionality
============

File Description
--------------------
*  `gmii_2_rgmii.v`: converting unsigned char to unsigned short.
*  `rgmii_rx1.v`: recieving packets in the on-chip using one land.
*  `rgmii_rx2.v`: recieving packets in the on-chip using two lands.
*  `rgmii_tx1.v`: transferring data to the off-chip using one land.
*  `rgmii_tx2.v`: transferring data to the off-chip using two lands.
*  `udp_rx.v`: parsing packets using the UDP protocol to extract packet fields and construct stream items.
*  `udp_top.v`: the top funtion of udp_rx.v.

Experimental setup
--------------------
* compile: Vivado 2020
* language: Verilog
