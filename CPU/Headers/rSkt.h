#ifndef MIME_RSKT_H
#define MIME_RSKT_H
#define KEY_LEN 16
#include "Sketch.h"
#include "MurmurHash3.h"
#include "Params.h"
#include <cstring>
#include <ctime>
#include <cmath>
#define MAX(a,b) ((a)<(b))?(b):(a)
#include <cstring>
#include <string>
#define KEY_LEN 16


class rSkt : public Sketch{
private:
    uint32_t w, m, num_leading_zeros;   // w is the length of C and C', m is the number of registers in C[i]
    uint32_t ** C, ** C1;
    uint32_t keyseed, eleseed;
    double alpha;
public:
    rSkt(uint32_t, uint32_t);
    ~rSkt() {
        for (int i = 0; i < w; ++i) {
            delete[] C[i];
            delete[] C1[i];
        }
    }

    void update(uint32_t, uint32_t, uint32_t);
    int query(uint32_t*, uint32_t*);
    int estimate(uint32_t , int);
};
#endif //MIME_RSKT_H
