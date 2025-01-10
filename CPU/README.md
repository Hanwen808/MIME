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
│   ├── BF_TCM.h
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
```

## Requirements

- CMake 3.26 or above
- g++ 7.5.0 or above
- Compiler with support for C++17 standard
