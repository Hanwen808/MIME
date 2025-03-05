#include "../Headers/MIME.h"

// Generate function of MIME
MIME::MIME(int BIT_LEN, float p) {
    this->length = BIT_LEN;
    this->bitmap = allocbitmap(length);
    fillzero(bitmap, length);
    this->p = p;
    this->post = p;
    this->counter = 0;
    this->splitIndex = ceilf(1.0 / this->p);
}

void MIME::build() {
    for (auto srciter = Supercube.begin(); srciter != Supercube.end(); srciter ++) {
        for (auto dstiter = srciter->second.begin(); dstiter != srciter->second.end(); dstiter ++) {
            invSupercube[dstiter->first][srciter->first] = Supercube[srciter->first][dstiter->first];
        }
    }
}

// Updating the filter
void MIME::update(uint32_t flowid, uint32_t eleid, uint32_t portid) {
    char hash_input_xor[5] = {0};       // XOR of flow id, element id and port id.
    uint32_t xor_val = flowid ^ eleid ^ portid;
    uint32_t hashValue, hashIndex;      // Record the high 32bits and low 32bits hash value of murmurhash3
    memcpy(hash_input_xor, &xor_val, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_xor, 4, 12412, &hashValue);
    hashIndex = hashValue % length;
    if (!getbit(hashIndex, bitmap)) {
        setbit(hashIndex, bitmap);      // update the associated hashed bit
        counter ++;                     // update the counter recorded the number of one-bit
        if (hashIndex < length * post) {
            // Sending this non-duplicate to the off-chip memory
            Supercube[flowid][eleid].insert(portid);
            sampleNum += 1;
        }
        post = (p * length) / (length - counter); // update the post-sampling rate in MIME
    }
}

// Estimation of MIME
int MIME::estimate(uint32_t key, int task) {
    float estimatedValue = 0.0;
    std::unordered_map<int, int> numsDict;
    std::unordered_map<uint32_t , int> keyCounts;
    std::unordered_map<uint32_t , std::unordered_set<uint32_t>> columnMap;
    switch (task) {
        case 0: {
            // Per-source destination flow spread estimation
            columnMap = Supercube[key];
            for (auto iter = columnMap.begin(); iter != columnMap.end() ; iter++)
                numsDict[(iter->second).size()] += 1;
            break;
        }
        case 1: {
            // Per-source port flow estimation
            columnMap = Supercube[key];
            std::unordered_map<uint32_t, uint32_t> portMulDict;
            for (auto iter = columnMap.begin(); iter != columnMap.end(); iter++) {
                for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); iter2 ++) {
                    portMulDict[*iter2] += 1;
                }
            }
            for (auto iter = portMulDict.begin(); iter != portMulDict.end(); iter ++)
                numsDict[iter->second] += 1;
            break;
        }
        case 2: {
            // Per-destination source flow estimation
            columnMap = invSupercube[key];
            for (auto iter = columnMap.begin(); iter != columnMap.end() ; iter++)
                numsDict[(iter->second).size()] += 1;
            break;
        }
        default:
            break;
    }

    for (auto iter = numsDict.begin(); iter != numsDict.end(); iter ++)
        if(iter->first < this->splitIndex)
            estimatedValue += (iter->second) / (1 - pow((1 - this->p), 1.0 * (iter->first)));
        else
            estimatedValue += (iter->second) / (1 - pow((1 - this->p), 1.0 * (iter->first) / this->p));
    return ceilf(estimatedValue);
}

MIME::~MIME() {
    if (bitmap)
        delete bitmap;
}