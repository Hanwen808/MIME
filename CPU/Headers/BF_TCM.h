//
// Created by lenovo on 2025/1/9.
//

#ifndef TCMSKETCH_BF_TCM_H
#define TCMSKETCH_BF_TCM_H
#include "Sketch.h"
#include "TCM.h"
#include "bitmap.h"
#include <unordered_set>
#define KEY_SIZE 16
class BFTCM:public Sketch {
private:
    TCM* tcm;
    bitmap B;
    uint32_t mem, mem_filter, mem_tcm, bits;
    uint32_t filter_k, tcm_k;
    float ratio;
    uint32_t* filter_seeds;
public:
    BFTCM(uint32_t mem, float ratio, uint32_t k, uint32_t hash_num) {
        this->mem = mem;
        this->ratio = ratio;
        this->mem_filter = static_cast<uint32_t>(mem * ratio);
        this->mem_tcm = mem - mem_filter;
        filter_k = k;
        tcm_k = hash_num;
        uint32_t d = static_cast<uint32_t>(sqrt((1.0 * mem_tcm * 1024 * 8 / 8.0) / tcm_k));
        tcm = new TCM(d, d, tcm_k);
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

#endif //TCMSKETCH_BF_TCM_H
