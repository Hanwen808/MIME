cmake_minimum_required(VERSION 3.10)
project(MIME)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ../)
set(CMAKE_CXX_FLAGS "-O3")
#MIME compile
add_executable(MIME MIME_main.cpp ./Sources/bitmap.cpp ./Sources/MurmurHash3.cpp ./Sources/MIME.cpp)
#CSE compile
#add_executable(MIME CSE_main.cpp ./Sources/bitmap.cpp ./Sources/MurmurHash3.cpp ./Sources/CSE.cpp)
#vHLL compile
#add_executable(MIME vHLL_main.cpp ./Sources/vHLL.cpp ./Sources/MurmurHash3.cpp)
#rSkt compile
#add_executable(MIME rSkt_main.cpp ./Sources/rSkt.cpp ./Sources/MurmurHash3.cpp)
#Supersketch compile
#add_executable(MIME Supersketch_main.cpp ./Sources/Supersketch.cpp ./Sources/MurmurHash3.cpp)
