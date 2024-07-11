#include "../Headers/rSkt.h"
#include <iostream>

rSkt::rSkt(uint32_t w, uint32_t m) {
    this->w = w;
    this->m = m;
    this->C = new uint32_t *[w];
    this->C1 = new uint32_t *[w];
    for (int i = 0; i < w; ++i) {
        C[i] = new uint32_t[m] {0};
        C1[i] = new uint32_t[m] {0};
    }
    keyseed = 41213;
    eleseed = 12412;
    num_leading_zeros = floor(log10(double(m)) / log10(2.0)); // used to locate
    /*memset(C, 0, sizeof C);
    memset(C1, 0, sizeof C1);*/
    if (m == 16) {
        alpha = 0.673;
    } else if (m == 32) {
        alpha = 0.697;
    } else if (m == 64) {
        alpha = 0.709;
    } else {
        alpha = (0.7213 / (1 + (1.079 / m)));
    }
}

void rSkt::update(uint32_t key, uint32_t ele, uint32_t others) {
    uint32_t hashValue, hashIndex, hashValue2;
    uint32_t g_f_i;
    char hash_input_key[5] = {0};
    char hash_input_ele[5] = {0};
    memcpy(hash_input_key, &key, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_key, 4, keyseed, &hashValue);
    hashIndex = hashValue % w;
    memcpy(hash_input_ele, &ele, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_ele, 4, eleseed, &hashValue2);
    uint32_t p_part = hashValue2 >> (sizeof(uint32_t) * 8 - num_leading_zeros); // hashed virtual register
    uint32_t q_part = hashValue2 - (p_part << (sizeof(uint32_t) * 8 - num_leading_zeros));
    uint32_t left_most = 0;
    while(q_part) {
        left_most += 1;
        q_part = q_part >> 1;
    }
    left_most = sizeof(uint32_t) * 8 - num_leading_zeros - left_most + 1;
    MurmurHash3_x86_32(hash_input_key, 4, p_part, &hashValue);
    g_f_i = hashValue % 2;
    if (g_f_i == 0) {
        C[hashIndex][p_part] = MAX(left_most, C[hashIndex][p_part]);
    } else {
        C1[hashIndex][p_part] = MAX(left_most, C1[hashIndex][p_part]);
    }
}

int rSkt::query(uint32_t * Lf, uint32_t * Lf1) {
    double sum_register_Lf = 0;
    double sum_register_Lf1 = 0;
    double zero_ratio_Lf = 0, zero_ratio_Lf1 = 0;
    for (int i = 0; i < m; ++i) {
        sum_register_Lf += pow(2.0, -double(Lf[i]));
        if(Lf[i] == 0)
            zero_ratio_Lf += 1;
        sum_register_Lf1 += pow(2.0, -double(Lf1[i]));
        if (Lf1[i] == 0)
            zero_ratio_Lf1 += 1;
    }
    zero_ratio_Lf = zero_ratio_Lf1 / m;
    zero_ratio_Lf1 = zero_ratio_Lf1 / m;
    double n = alpha * pow(double(m), 2) / sum_register_Lf;
    double n_ = alpha * pow(double(m), 2) / sum_register_Lf1;
    if(n <= 2.5 * m) {
        if(zero_ratio_Lf != 0) {
            n = - double(m) * log(zero_ratio_Lf);
        }
    }
    else if(n > pow(2.0, 32) / 30) {
        n = - pow(2.0, 32) * log(1 - n / pow(2.0, 32));
    }

    if(n_ <= 2.5 * m) {
        if(zero_ratio_Lf1 != 0) {
            n_ = - double(m) * log(zero_ratio_Lf1);
        }
    }
    else if(n_ > pow(2.0, 32) / 30) {
        n_ = - pow(2.0, 32) * log(1 - n_ / pow(2.0, 32));
    }
    return MAX(n - n_, 0);
}

int rSkt::estimate(uint32_t key, int task) {
    uint32_t hashValue, hashIndex, g_f_i, g_f_i_hashValue;
    uint32_t * Lf, *Lf1;
    Lf = new uint32_t[m]{0};
    Lf1 = new uint32_t[m]{0};
    char hash_input_key[5] = {0};
    memcpy(hash_input_key, &key, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_key, 4, keyseed, &hashValue);
    hashIndex = hashValue % w;
    for (int i = 0; i < m; ++i) {
        MurmurHash3_x86_32(hash_input_key, 4, i, &g_f_i_hashValue);
        g_f_i = g_f_i_hashValue % 2;
        if (g_f_i == 0) {
            Lf[i] = C[hashIndex][i];
            Lf1[i] = C1[hashIndex][i];
        } else {
            Lf[i] = C1[hashIndex][i];
            Lf1[i] = C[hashIndex][i];
        }
    }
    return this->query(Lf, Lf1);
}