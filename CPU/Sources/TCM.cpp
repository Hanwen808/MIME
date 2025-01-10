//
// Created by lenovo on 2025/1/9.
//
#include "../Headers/TCM.h"

TCM::TCM(uint32_t w,uint32_t d,uint32_t h)
{
    width = w;
    depth = d;
    hashnum = h;
    value = new int*[hashnum];
    //mapTable = new hashTable<string>[hashnum];
    for (int i=0; i<hashnum; ++i)
    {
        value[i] = new int[width*depth];
        memset(value[i],0,sizeof(int)*width*depth);
        /*if(usetable)
		mapTable[i].init(tablesize);*/
    }
    row_seed = 31231;
    col_seed = 41231;
}


void TCM::update(uint32_t src, uint32_t dst, uint32_t dport) {
    for (int i = 0; i < hashnum; i++) {
        uint32_t hashValue1, hashIndex1;
        uint32_t hashValue2, hashIndex2;
        MurmurHash3_x86_32(&src, 4, row_seed, &hashValue1);
        MurmurHash3_x86_32(&dst, 4, col_seed, &hashValue2);
        /*if(usetable)
        {mapTable[i].insert(hash1, std::string(reinterpret_cast<const char*>(v1)));
        mapTable[i].insert(hash2, std::string(reinterpret_cast<const char*>(v2)));
        }*/
        hashIndex1 = hashValue1 % depth;
        hashIndex2 = hashValue2 % width;
        value[i][hashIndex1 * width + hashIndex2] += 1;

        //mapTable[i].insert(hash1, string(reinterpret_cast<const char*>(v1)));
        //mapTable[i].insert(hash2, string(reinterpret_cast<const char*>(v2)));

    }
}

uint32_t TCM::estimate_psd(uint32_t src) {
    uint32_t hashIndex, hashValue;
    uint32_t zero_bits = INT32_MAX;
    for (int i = 0; i < 1; ++i) {
        MurmurHash3_x86_32(&src, 4, row_seed, &hashValue);
        hashIndex = hashValue % depth;
        uint32_t zero_counts = 0;
        for (int j = 0; j < width; ++j) {
            if (value[i][hashIndex * width + j] == 0)
                zero_counts ++;
        }
        if (zero_counts < zero_bits)
            zero_bits = zero_counts;
    }
    double res;
    if (zero_bits == 0) {
        res = this->width * log(1.0 * this->width);
    } else
        res = -this->width * log((1.0 * zero_bits) / (1.0 * this->width));
    return static_cast<uint32_t>(res);
}

uint32_t TCM::estimate_psdp(uint32_t src) {
    uint32_t hashIndex, hashValue;
    uint32_t est_val_max = 0;
    for (int i = 0; i < 1; ++i) {
        MurmurHash3_x86_32(&src, 4, row_seed, &hashValue);
        hashIndex = hashValue % depth;
        uint32_t est_val = 0;
        for (int j = 0; j < width; ++j) {
            est_val += value[i][hashIndex * width + j];
        }
        if (est_val >= est_val_max)
            est_val_max = est_val;
    }
    return est_val_max;
}

uint32_t TCM::estimate_pds(uint32_t dst) {
    uint32_t hashIndex, hashValue;
    uint32_t zero_bits = INT32_MAX;
    for (int i = 0; i < 1; ++i) {
        MurmurHash3_x86_32(&dst, 4, row_seed, &hashValue);
        hashIndex = hashValue % width;
        uint32_t zero_counts = 0;
        for (int j = 0; j < depth; ++j) {
            if (value[i][hashIndex + j * width] == 0)
                zero_counts ++;
        }
        if (zero_counts < zero_bits)
            zero_bits = zero_counts;
    }
    double res;
    if (zero_bits == 0) {
        res = this->depth * log(1.0 * this->depth);
    } else
        res = -this->depth * log((1.0 * zero_bits) / (1.0 * this->depth));
    return static_cast<uint32_t>(res);
}