#include "./murmurhash.h"
#include "./bitmap.h"
#include <stdlib.h>
#define KEY_SIZE 16
#define BITMAP_LEN 819200

uint8_t* init() {
    uint8_t* bitmap = allocbitmap(BITMAP_LEN);
    return bitmap;
}

void update(uint8_t* bitmap, uint32_t key, uint32_t ele, float* post, float p, uint32_t* c) {
    uint32_t hashValue, hashIndex;
    uint32_t XOR = key ^ ele;
    MurmurHash3_x86_32(XOR, 0, &hashValue);
    hashIndex = hashValue % BITMAP_LEN;
    if (!getbit(hashIndex, bitmap)) {
        setbit(hashIndex, bitmap);
        *c = *c + 1;
        if (hashIndex <= BITMAP_LEN * (*post)) {
            // off-chip
        }
        *post = (BITMAP_LEN * p) / (BITMAP_LEN - (*c));
    }
}
