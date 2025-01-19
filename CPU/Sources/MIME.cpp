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

// Updating the filter
void MIME::update(uint32_t flowid, uint32_t eleid, uint32_t portid) {
    char hash_input_xor[5] = {0};       // XOR of flow id, element id and port id.
    uint32_t xor_val = flowid ^ eleid ^ portid;
    uint32_t hashValue, hashIndex;      // Record the high 32bits and low 32bits hash value of murmurhash3
    memcpy(hash_input_xor, &xor_val, sizeof(uint32_t));
    MurmurHash3_x86_32(hash_input_xor, 4, 12412, &hashValue);
    // in most scenario, the optimal hash function is one. So we only test the throughput with one hash function,
    // for optimal hash function number is more than one, we provide cores in Python_codes/ directory.
    hashIndex = hashValue % length;
    if (!getbit(hashIndex, bitmap)) {
        setbit(hashIndex, bitmap);      // update the associated hashed bit
        counter ++;                     // update the counter recorded the number of one-bit
        if (hashIndex < length * post) {
            // Sending this non-duplicate to the off-chip memory
            //SupercubeDC[flowid][eleid].insert(portid);
            //SupercubeDPC[flowid][portid].insert(eleid);
            //SupercubeSC[eleid][flowid].insert(portid);
            //sampleNum += 1;
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
        case 0:
            // Per-source destination flow spread estimation
            columnMap = SupercubeDC[key];
            break;
        case 1:
            // Per-source port flow estimation
            columnMap = SupercubeDPC[key];
            break;
        case 2:
            // Per-destination source flow estimation
            columnMap = SupercubeSC[key];
            break;
        default:
            break;
    }
    for (auto iter = columnMap.begin(); iter != columnMap.end() ; iter++)
        numsDict[(iter->second).size()] += 1;
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