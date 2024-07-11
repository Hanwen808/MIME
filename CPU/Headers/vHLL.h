#ifndef MIME_VHLL_H
#define MIME_VHLL_H
#define KEY_LEN 16
#include "Sketch.h"
#include "MurmurHash3.h"
#include "Params.h"
#include <set>
#include <ctime>
#include <cmath>
#include <cstring>
#define MAX(a,b) ((a)<(b))?(b):(a)

class vHLL : public Sketch {
private:
    uint32_t m, v, num_leading_zeros;
    uint32_t* R, *S;
    uint32_t seed, cardi_all_flow;
    double alpha;
public:
    vHLL(uint32_t, uint32_t);
    ~vHLL() {
        delete R;
        delete S;
    }
    void update(uint32_t, uint32_t, uint32_t);
    int estimate(uint32_t, int);
    void update_param();
};
#endif //MIME_VHLL_H
