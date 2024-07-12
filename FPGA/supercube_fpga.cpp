#include "./murmurhash.h"
#include "./bitmap.h"
#include <stdlib.h>
#define BITMAP_LEN 204800
unsigned char B[BITMAP_LEN] = {0};

uint8_t* init() {
    uint8_t* bitmap = allocbitmap(BITMAP_LEN);
    return bitmap;
}

void update(uint32_t src_i, uint32_t dst_i, uint32_t sport_i, uint32_t dport_i, float* post, float p, uint32_t* c, uint32_t* src_o, uint32_t* dst_o, uint32_t* sport_o, uint32_t* dport_o) {
    uint32_t hashValue, hashIndex;
    uint32_t XOR = src_i ^ dst_i ^ sport_i ^ dport_i;
    MurmurHash3_x86_32(&XOR, 0, &hashValue);
    hashIndex = hashValue % BITMAP_LEN;
    if (!getbit(hashIndex, B)) {
        setbit(hashIndex, B);
        *c = *c + 1;
        if (hashIndex <= BITMAP_LEN * (*post)) {
            *src_o = src_i;
            *dst_o = dst_i;
            *sport_o = sport_i;
            *dport_o = dport_i;
        }
        *post = (BITMAP_LEN * p) / (BITMAP_LEN - (*c));
    }
}
