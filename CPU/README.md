# C++ implementation

This is a C++ implementation for MIME and related solutions.

## Project Structure

```
MIME_Cpp/
├── MIME_main.cpp
├── CSE_main.cpp
├── Supersketch_main.cpp
├── rSkt_main.cpp
├── vHLL_main.cpp
├── ipv4.cpp
├── Headers/
│   ├── MurmurHash3.h
│   ├── CSE.h
│   ├── MIME.h
│   ├── Supersketch.h
│   ├── bitmap.h
│   ├── rSkt.h
│   ├── Params.h
│   ├── Sketch.h
│   ├── TCM.h
│   ├── BF_TCM.h
│   └── vHLL.h
├── Sources/
│   ├── CSE.cpp
│   ├── MIME.cpp
│   ├── MurmurHash3.cpp
│   ├── Supersketch.cpp
│   ├── bitmap.cpp
│   ├── rSkt.cpp
│   ├── TCM.cpp
│   ├── BF_TCM.cpp
│   └── vHLL.cpp
```

## Usage

### Compilation
If you want to compile MIME and other algorithms using CMake, the following commands should be executed.
```bash
$ mkdir build
$ cd build
$ cmake ..
$ make
```

If you want to compile MIME and other algorithms using g++, the followding commands should be execueted.
Note that, the xxx.sh is a bash shell file including g++ compile codes with optimize_flag $-O3$.
```shell
../scripts/MIME.sh  # MIME
../scripts/CSE.sh   # CSE
../scripts/vHLL.sh  # vHLL
../scripts/rSkt.sh  # rSkt
../scripts/Supersketch.sh  # supersketch
../scripts/BF_TCM.sh #BF+TCM
```

## Requirements

- CMake 3.26 or above
- g++ 7.5.0 or above
- Compiler with support for C++17 standard

## Acknowledgement
Other baseline methods are implemented based on following papers:
- **CSE**: M. Yoon, T. Li, S. Chen, J. . -K. Peir. "Fit a Spread Estimator in Small Memory". Proc. of IEEE INFOCOM, 2009.
- **vHLL**: Qingjun Xiao, Shigang Chen, You Zhou, Min Chen, Junzhou Luo, Tengli Li, Yibei Ling. "Cardinality Estimation for Elephant Flows: A Compact Solution Based on Virtual Register Sharing". IEEE/ACM Transactions on Networking, 25(6): 3738-3752 (2017).
- **rSkt**: Haibo Wang, Chaoyi Ma, Olufemi O. Odegbile, Shigang Chen, Jih-Kwon Peir. "Randomized Error Removal for Online Spread Estimation in High-Speed Networks". IEEE/ACM Transactions on Networking, 31(2): 558-573 (2023).
- **Supersketch**: Xuyang Jing, Hui Han, Zheng Yan, Witold Pedrycz. "SuperSketch: A Multi-Dimensional Reversible Data Structure for Super Host Identification". IEEE Transactions on Dependable and Secure Computing, 19(4): 2741-2754 (2022).
