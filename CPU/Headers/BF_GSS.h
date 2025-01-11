//
// Created by Hanwen on 2025/1/10.
//

#ifndef BF_GSS_H
#define BF_GSS_H
#include "Sketch.h"
#include "GSS.h"
#include "bitmap.h"
#include <unordered_set>
#define KEY_SIZE 16
class BFGSS:public Sketch {
private:
    GSS* gss;
    bitmap B;
    uint32_t mem, mem_filter, mem_gss, bits;
    uint32_t filter_k, gss_k;
    float ratio;
    uint32_t* filter_seeds;
public:
    BFGSS(uint32_t mem, float ratio, uint32_t k, uint32_t hash_num) {
        this->mem = mem;
        this->ratio = ratio;
        this->mem_filter = static_cast<uint32_t>(mem * ratio);
        this->mem_gss = mem - mem_filter;
        filter_k = k;
        gss_k = hash_num;
        uint32_t d = static_cast<uint32_t>(sqrt((1.0 * mem_gss * 1024 * 8 / 80.0) / gss_k));
        gss = new GSS(d, 2, 1, 1, 16);
        bits = mem_filter * 1024 * 8;
        B = allocbitmap(bits);
        filter_seeds = new uint32_t[10];
        std::unordered_set<uint32_t> seed_set;
        while (seed_set.size() != filter_k) {
            srand(time(NULL));
            seed_set.insert(1000 * rand() % 10000);
        }
        int no = 0;
        for (auto iter = seed_set.begin(); iter != seed_set.end(); ++iter) {
            filter_seeds[no ++] = *iter;
        }
    }
    void update(uint32_t src, uint32_t dst, uint32_t dport);
    int estimate(uint32_t key, int task);
};

#endif //BF_GSS_H
