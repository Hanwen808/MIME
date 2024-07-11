#ifndef MIME_SKETCH_H
#define MIME_SKETCH_H
#include <stdint.h>

class Sketch {
public:
    virtual void update(uint32_t, uint32_t, uint32_t) = 0;
    virtual int estimate(uint32_t, int ) = 0;
};
#endif //MIME_SKETCH_H
