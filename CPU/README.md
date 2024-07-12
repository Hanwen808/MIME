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
│   └── vHLL.h
├── Sources/
│   ├── CSE.cpp
│   ├── MIME.cpp
│   ├── MurmurHash3.cpp
│   ├── Supersketch.cpp
│   ├── bitmap.cpp
│   ├── rSkt.cpp
│   └── vHLL.cpp
```

## Usage

### Compilation

```bash
$ mkdir build
$ cd build
$ cmake ..
$ make
$ ../scripts/xxx.sh
```

## Requirements

- CMake 3.26 or above
- Compiler with support for C++17 standard
