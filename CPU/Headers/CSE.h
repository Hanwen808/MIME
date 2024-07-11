#ifndef MIME_CSE_H
#define MIME_CSE_H
#define KEY_LEN 16
#include "MurmurHash3.h"
#include "Sketch.h"
#include "bitmap.h"
#include "cmath"
#include "ctime"
#include "cstring"
#include "stdlib.h"

class CSE : public Sketch {
private:
    uint32_t m, v;   // the number of bits in physical bitmap and virtual bitmap
    uint8_t* bitmap; // the physical bitmap
    uint32_t c;      // the counter that counts zero bits in bitmap
    uint32_t seed;
public:
    CSE(uint32_t , uint32_t);
    ~CSE() {
        delete bitmap;
    }
    void update(uint32_t, uint32_t, uint32_t);
    int  estimate(uint32_t , int );
};
#endif //MIME_CSE_H
