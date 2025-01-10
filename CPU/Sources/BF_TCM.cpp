//
// Created by lenovo on 2025/1/9.
//
#include "../Headers/BF_TCM.h"

void BFTCM::update(uint32_t src, uint32_t dst, uint32_t dport) {
    uint32_t xor_val = src ^ dst ^ dport;
    bool flag = false;
    for (int i = 0; i < filter_k; ++i) {
        uint32_t hashValue, hashIndex;
        MurmurHash3_x86_32(&xor_val, 4, filter_seeds[i], &hashValue);
        hashIndex = hashValue % bits;
        if (getbit(hashIndex, B) == 0) {
            setbit(hashIndex, B);
            flag = true;
        }
    }
    if (flag) {
        tcm->update(src, dst, dport);
    }
}

int BFTCM::estimate(uint32_t key, int task) {
    if (task == 0) {
        return tcm->estimate_psd(key);
    } else if (task == 1) {
        return tcm->estimate_psdp(key);
    } else if (task == 2) {
        return tcm->estimate_pds(key);
    }
}