#include "../Headers/vHLL.h"
vHLL::vHLL(uint32_t m, uint32_t v) {
    this->m = m;
    this->v = v;
    this->S = new uint32_t[v];
    this->R = new uint32_t[m];
    memset(R, 0, sizeof R);
    srand(NULL);
    std::set<uint32_t> seeds;
    uint32_t index = 0;
    while (seeds.size() < v)
        seeds.insert(uint32_t(rand()));
    for (auto iter = seeds.begin(); iter != seeds.end(); ++iter)
        S[index ++] = *iter;
    num_leading_zeros = floor(log10(double(v)) / log10(2.0)); // used to locate
    seed = uint32_t(rand());
    if (v == 16) {
        alpha = 0.673;
    } else if (v == 32) {
        alpha = 0.697;
    } else if (v == 64) {
        alpha = 0.709;
    } else {
        alpha = (0.7213 / (1 + (1.079 / v)));
    }
    cardi_all_flow = 0;
}

void vHLL::update(uint32_t key, uint32_t ele, uint32_t others) {
    uint32_t hashValue, hashIndex;
    char hash_input_key[5] = {0};
    char hash_input_ele[5] = {0};
    memcpy(hash_input_key, &key, sizeof(uint32_t));
    memcpy(hash_input_ele, &ele, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_ele, 4, seed, &hashValue);
    uint32_t p_part = hashValue >> (sizeof(uint32_t) * 8 - num_leading_zeros); // hashed virtual register
    uint32_t q_part = hashValue - (p_part << (sizeof(uint32_t) * 8 - num_leading_zeros));
    uint32_t left_most = 0;
    while(q_part) {
        left_most += 1;
        q_part = q_part >> 1;
    }
    left_most = sizeof(uint32_t) * 8 - num_leading_zeros - left_most + 1;
    MurmurHash3_x86_32(hash_input_key, 4, S[p_part], &hashValue);
    hashIndex = hashValue % m;
    R[hashIndex] = MAX(R[hashIndex], left_most);
}

void vHLL::update_param() {
    double zero_ratio = 0;
    double sum_register_arr = 0;
    for(int i = 0; i < m; i++) {
        sum_register_arr += pow(2.0, -double(R[i]));
        if(R[i] == 0)
            zero_ratio += 1;
    }
    zero_ratio = zero_ratio / m;
    double temp_cardi_all_flow = (0.7213 / (1 + (1.079 / m))) * pow(double(m), 2) / sum_register_arr;

    if(temp_cardi_all_flow <= 2.5 * m) {
        if(zero_ratio != 0) {
            cardi_all_flow = - double(m) * log(zero_ratio);
        }
    }
    else if(temp_cardi_all_flow > pow(2.0, 32) / 30) {
        cardi_all_flow = - pow(2.0, 32) * log(1 - temp_cardi_all_flow / pow(2.0, 32));
    }
    else if(temp_cardi_all_flow < pow(2.0, 32) / 30) {
        cardi_all_flow = temp_cardi_all_flow;
    }
}

int vHLL::estimate(uint32_t key, int task) {
    double zero_ratio_v_reg = 0;
    double sum_v_reg = 0;
    char hash_input_key[5] = {0};
    memcpy(hash_input_key, &key, sizeof(uint32_t));
    uint32_t hashValue, hashIndex;
    for(int i = 0; i < v; i++) {
        MurmurHash3_x86_32(hash_input_key, 4, S[i], &hashValue);
        hashIndex = hashValue % m;
        sum_v_reg += pow(2.0, -double(R[hashIndex]));
        if(R[hashIndex] == 0)
            zero_ratio_v_reg += 1;
    }
    zero_ratio_v_reg = zero_ratio_v_reg / v;
    double flow_cardi = alpha * pow(v, 2) / sum_v_reg;
    if(flow_cardi <= 2.5 * v) {
        if(zero_ratio_v_reg != 0)
            flow_cardi = - log(zero_ratio_v_reg) * v - cardi_all_flow * v / m;
        else
            flow_cardi = flow_cardi - cardi_all_flow * v / m;
    } else if(flow_cardi > pow(2.0, 32) / 30)
        flow_cardi = - pow(2.0, 32) * log(1 - flow_cardi / pow(2.0, 32)) - cardi_all_flow * v / m;
    else if(flow_cardi < pow(2.0, 32) / 30)
        flow_cardi = flow_cardi - cardi_all_flow * v / m;

    if (flow_cardi < 0) flow_cardi = 0;
    return flow_cardi;
}