# Multi-Information sampling and Mixed Estimation

This is the repository for source codes of MIME.

## Introduction
Spread measurement is an essential problem in high-speed networks with broad applications, such as anomalies detection and traffic engineering. 
In most scenarios, network administrators need to concurrently monitor the spreads of different types of flows to identify various abnormal activities.
Although many studies have designed memory-efficient structures, i.e., sketches, for the specified per-flow spread measurement, they have to deploy multiple sketches to support diverse per-flow spread measurements, resulting in significant memory and computational overhead.
This paper introduces an efficient multi-flow information compression method to simultaneously estimate differently defined flow spreads.
We only deploy one sketch to capture the varied spread information from each arrival packet by one pass and store them in the off-chip memory, thereby conserving on-chip memory and computational resources.
Additionally, we carefully design a multi-dimensional structure called Supercube to record varied spread information into different dimensions. 
By expanding the dimension of Supercube, we can simultaneously measure the spread of an arbitrary number and variety of flows.
We implement our estimator in hardware using NetFPGA.
Experiments based on real Internet traces show that our method reduces the average relative error by 83.36% for per-destination source flow spread estimation compared to rSkt (SOTA) with 300KB of on-chip memory, and increases update throughput 251.252-fold compared to Supersketch.
Moreover, our method can be expanded to support real-time detection of super hosts and novel super k-persistent spread measurement.
