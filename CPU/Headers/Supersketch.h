#ifndef MIME_SUPERSKETCH_H
#define MIME_SUPERSKETCH_H
#include "Sketch.h"
#include "MurmurHash3.h"
#include "Params.h"
#include <cstring>
#include <unordered_map>
#include <unordered_set>
#define KEY_LEN 16
#define MAX(a,b) ((a)<(b))?(b):(a)
#define MIN(a,b) ((a)<(b))?(a):(b)
typedef std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> Bitcube;

typedef std::unordered_map<uint32_t, std::unordered_set<uint32_t>> Flags;

class Supersketch : public Sketch {
private:
    uint32_t num; // the number of bitcubes
    uint32_t * P, *U;
    /*Bitcube* B;   // record the bits in all bitcubes
    Flags* rowF;  // record the hashed rows used to reverse ipv4
    Flags* colF;  // record the hashed columns used to reverse ipv4*/
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> B0;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> B1;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> B2;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> B3;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> B4;

    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> invB0;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> invB1;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> invB2;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> invB3;
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> invB4;

    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> rowF0;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> rowF1;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> rowF2;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> rowF3;

    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> colF0;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> colF1;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> colF2;
    std::unordered_map<uint32_t, std::unordered_set<uint32_t>> colF3;
public:
    Supersketch(uint32_t, uint32_t*, uint32_t*);
    ~Supersketch() {
        delete P;
        delete U;
    }
    void update(uint32_t, uint32_t, uint32_t);
    int estimate(uint32_t, int );
    void initInvbitcube();
};

#endif //MIME_SUPERSKETCH_H
