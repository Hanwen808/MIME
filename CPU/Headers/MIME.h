#ifndef MIME_MIME_H
#define MIME_MIME_H
#define PORT_SIZE 16
#define KEY_SIZE 16
#define XOR_SIZE 16
#include <iostream>
#include <string.h>
#include <cmath>
#include "Params.h"
#include "bitmap.h"
#include "Sketch.h"
#include "MurmurHash3.h"
#include <unordered_map>
#include <unordered_set>

class MIME : public Sketch {
private:
    uint8_t* bitmap;
    int counter;    // Counts the number of one-bit in the filter
    int length;     // The length of filter
    float post, p;  // p is the overall sampling rate in MIME, post is the adaptive-sampling rate
    int splitIndex;
    // Supercube implemented by hash table in off-chip memory used to record the sampled non-duplicates
    std::unordered_map<uint32_t , std::unordered_map<uint32_t , std::unordered_set<uint32_t>>> SupercubeDC;
    std::unordered_map<uint32_t , std::unordered_map<uint32_t , std::unordered_set<uint32_t>>> SupercubeDPC;
    std::unordered_map<uint32_t , std::unordered_map<uint32_t , std::unordered_set<uint32_t>>> SupercubeSC;
public:
    MIME(int, float);
    ~MIME();
    // Updating and sampling non-duplicates to the off-chip memory
    void update(uint32_t, uint32_t, uint32_t);
    // Estimation of MIME
    int estimate(uint32_t , int);
    int sampleNum = 0;
};

#endif //MIME_MIME_H
