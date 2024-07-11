#include "../Headers/Supersketch.h"
#include <string>
#include <vector>
#include <cmath>
#define MAXN32 0x7fffffff

Supersketch::Supersketch(uint32_t num, uint32_t * P, uint32_t * U) {
    this->num = num;
    this->P = new uint32_t[num];
    this->U = new uint32_t[num];

    for (int i = 0; i < num; ++i) {
        this->P[i] = P[i];
        this->U[i] = U[i];
    }
}

void Supersketch::update(uint32_t src, uint32_t dst, uint32_t portid) {
    uint32_t row, col1, col2;
    for (unsigned int i = 0; i < num; ++i) {
        row = src % this->P[i];
        col1 = dst % this->P[i];
        col2 = portid % this->U[i];
        switch (i) {
            case 0:
                B0[row][col1].insert(col2);
                rowF0[row].insert(dst % P[i + 1]);
                colF0[col1].insert(src % P[i + 1]);
                break;
            case 1:
                B1[row][col1].insert(col2);
                rowF1[row].insert(dst % P[i + 1]);
                colF1[col1].insert(src % P[i + 1]);
                break;
            case 2:
                B2[row][col1].insert(col2);
                rowF2[row].insert(dst % P[i + 1]);
                colF2[col1].insert(src % P[i + 1]);
                break;
            case 3:
                B3[row][col1].insert(col2);
                rowF3[row].insert(dst % P[i + 1]);
                colF3[col1].insert(src % P[i + 1]);
                break;
            case 4:
                B4[row][col1].insert(col2);
                break;
        }
    }
}

int Supersketch::estimate(uint32_t key, int task) {
    std::vector<int> vt(num);
    switch (task) {
        case 0:
            for (int i = 0; i < num; ++i) {
                uint32_t row, ones_;
                double v;
                double est_i;
                switch (i) {
                    case 0:
                        est_i = 0.0;
                        row = key % P[0];
                        if (B0.count(row) > 0) {
                            ones_ = B0[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[0] - ones_) / P[0];
                                if (P[0] != ones_) {
                                    est_i = - (1.0 * P[0]) * log(v);
                                } else {
                                    est_i = (1.0 * P[0]) * log(1.0 * P[0]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[0] = static_cast<uint32_t> (est_i);
                        break;
                    case 1:
                        est_i = 0.0;
                        row = key % P[1];
                        if (B1.count(row) > 0) {
                            ones_ = B1[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[1] - ones_) / P[1];
                                if (P[1] != ones_) {
                                    est_i = - (1.0 * P[1]) * log(v);
                                } else {
                                    est_i = (1.0 * P[1]) * log(1.0 * P[1]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[1] = static_cast<uint32_t> (est_i);
                        break;
                    case 2:
                        est_i = 0.0;
                        row = key % P[2];
                        if (B2.count(row) > 0) {
                            ones_ = B2[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[2] - ones_) / P[2];
                                if (P[2] != ones_) {
                                    est_i = - (1.0 * P[2]) * log(v);
                                } else {
                                    est_i = (1.0 * P[2]) * log(1.0 * P[2]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[2] = static_cast<uint32_t> (est_i);
                        break;
                    case 3:
                        est_i = 0.0;
                        row = key % P[3];
                        if (B3.count(row) > 0) {
                            ones_ = B3[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[3] - ones_) / P[3];
                                if (P[3] != ones_) {
                                    est_i = - (1.0 * P[3]) * log(v);
                                } else {
                                    est_i = (1.0 * P[3]) * log(1.0 * P[3]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[3] = static_cast<uint32_t> (est_i);
                        break;
                    case 4:
                        est_i = 0.0;
                        row = key % P[4];
                        if (B4.count(row) > 0) {
                            ones_ = B4[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[4] - ones_) / P[4];
                                if (P[4] != ones_) {
                                    est_i = - (1.0 * P[4]) * log(v);
                                } else {
                                    est_i = (1.0 * P[4]) * log(1.0 * P[4]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[4] = static_cast<uint32_t> (est_i);
                        break;
                }
            }
            break;
        case 1:
            for (int i = 0; i < num; ++i) {
                uint32_t row;
                double v;
                double est_i;
                switch (i) {
                    case 0:
                        row = key % P[i];
                        if (B0.count(row) > 0) {
                            std::unordered_set<uint32_t> dpc_set;
                            for (auto iter = B0[row].begin(); iter != B0[row].end(); ++iter) {
                                for (auto iter2 = (iter->second).begin(); iter2 != (iter->second).end(); ++iter2) {
                                    dpc_set.insert(*iter2);
                                }
                            }
                            v = (1.0 * (U[i] - dpc_set.size())) / (1.0 * U[i]);
                            if (U[i] == dpc_set.size()) {
                                est_i = (1.0 * U[i]) * log(1.0 * U[i]);
                            } else {
                                est_i = -1.0 * U[i] * log(v);
                            }
                            if (est_i < 0) est_i = 0.0;
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 1:
                        row = key % P[i];
                        if (B1.count(row) > 0) {
                            std::unordered_set<uint32_t> dpc_set;
                            for (auto iter = B1[row].begin(); iter != B1[row].end(); ++iter) {
                                for (auto iter2 = (iter->second).begin(); iter2 != (iter->second).end(); ++iter2) {
                                    dpc_set.insert(*iter2);
                                }
                            }
                            v = (1.0 * (U[i] - dpc_set.size())) / (1.0 * U[i]);
                            if (U[i] == dpc_set.size()) {
                                est_i = (1.0 * U[i]) * log(1.0 * U[i]);
                            } else {
                                est_i = -1.0 * U[i] * log(v);
                            }
                            if (est_i < 0) est_i = 0.0;
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 2:
                        row = key % P[i];
                        if (B2.count(row) > 0) {
                            std::unordered_set<uint32_t> dpc_set;
                            for (auto iter = B2[row].begin(); iter != B2[row].end(); ++iter) {
                                for (auto iter2 = (iter->second).begin(); iter2 != (iter->second).end(); ++iter2) {
                                    dpc_set.insert(*iter2);
                                }
                            }
                            v = (1.0 * (U[i] - dpc_set.size())) / (1.0 * U[i]);
                            if (U[i] == dpc_set.size()) {
                                est_i = (1.0 * U[i]) * log(1.0 * U[i]);
                            } else {
                                est_i = -1.0 * U[i] * log(v);
                            }
                            if (est_i < 0) est_i = 0.0;
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 3:
                        row = key % P[i];
                        if (B3.count(row) > 0) {
                            std::unordered_set<uint32_t> dpc_set;
                            for (auto iter = B3[row].begin(); iter != B3[row].end(); ++iter) {
                                for (auto iter2 = (iter->second).begin(); iter2 != (iter->second).end(); ++iter2) {
                                    dpc_set.insert(*iter2);
                                }
                            }
                            v = (1.0 * (U[i] - dpc_set.size())) / (1.0 * U[i]);
                            if (U[i] == dpc_set.size()) {
                                est_i = (1.0 * U[i]) * log(1.0 * U[i]);
                            } else {
                                est_i = -1.0 * U[i] * log(v);
                            }
                            if (est_i < 0) est_i = 0.0;
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 4:
                        row = key % P[i];
                        if (B4.count(row) > 0) {
                            std::unordered_set<uint32_t> dpc_set;
                            for (auto iter = B4[row].begin(); iter != B4[row].end(); ++iter) {
                                for (auto iter2 = (iter->second).begin(); iter2 != (iter->second).end(); ++iter2) {
                                    dpc_set.insert(*iter2);
                                }
                            }
                            v = (1.0 * (U[i] - dpc_set.size())) / (1.0 * U[i]);
                            if (U[i] == dpc_set.size()) {
                                est_i = (1.0 * U[i]) * log(1.0 * U[i]);
                            } else {
                                est_i = -1.0 * U[i] * log(v);
                            }
                            if (est_i < 0) est_i = 0.0;
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                }
            }
            break;
        case 2:
            for (int i = 0; i < num; ++i) {
                uint32_t row, ones_;
                double v;
                double est_i;
                switch (i) {
                    case 0:
                        est_i = 0.0;
                        row = key % P[i]; // dst
                        if (invB0.count(row) > 0) {
                            ones_ = invB0[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[i] - ones_) / P[i];
                                if (P[i] != ones_) {
                                    est_i = - (1.0 * P[i]) * log(v);
                                } else {
                                    est_i = (1.0 * P[i]) * log(1.0 * P[i]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 1:
                        est_i = 0.0;
                        row = key % P[i]; // dst
                        if (invB1.count(row) > 0) {
                            ones_ = invB1[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[i] - ones_) / P[i];
                                if (P[i] != ones_) {
                                    est_i = - (1.0 * P[i]) * log(v);
                                } else {
                                    est_i = (1.0 * P[i]) * log(1.0 * P[i]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 2:
                        est_i = 0.0;
                        row = key % P[i]; // dst
                        if (invB2.count(row) > 0) {
                            ones_ = invB2[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[i] - ones_) / P[i];
                                if (P[i] != ones_) {
                                    est_i = - (1.0 * P[i]) * log(v);
                                } else {
                                    est_i = (1.0 * P[i]) * log(1.0 * P[i]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 3:
                        est_i = 0.0;
                        row = key % P[i]; // dst
                        if (invB3.count(row) > 0) {
                            ones_ = invB3[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[i] - ones_) / P[i];
                                if (P[i] != ones_) {
                                    est_i = - (1.0 * P[i]) * log(v);
                                } else {
                                    est_i = (1.0 * P[i]) * log(1.0 * P[i]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                    case 4:
                        est_i = 0.0;
                        row = key % P[i]; // dst
                        if (invB4.count(row) > 0) {
                            ones_ = invB4[row].size();
                            if (ones_ != 0) {
                                v = 1.0 * (P[i] - ones_) / P[i];
                                if (P[i] != ones_) {
                                    est_i = - (1.0 * P[i]) * log(v);
                                } else {
                                    est_i = (1.0 * P[i]) * log(1.0 * P[i]);
                                }
                                if (est_i < 0) est_i = 0.0;
                            }
                        }
                        vt[i] = static_cast<uint32_t> (est_i);
                        break;
                }
            }
    }
    uint32_t res = MAXN32;
    for (int i = 0; i < num; i++) {
        if (vt[i] < res) {
            res = vt[i];
        }
    }
    vt.clear();
    return res;
}

void Supersketch::initInvbitcube() {
    for (auto iter = B0.begin(); iter != B0.end(); iter ++) {
        for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); ++iter2) {
            invB0[iter2->first][iter->first] = iter2->second;
        }
    }
    for (auto iter = B1.begin(); iter != B1.end(); iter ++) {
        for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); ++iter2) {
            invB1[iter2->first][iter->first] = iter2->second;
        }
    }
    for (auto iter = B2.begin(); iter != B2.end(); iter ++) {
        for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); ++iter2) {
            invB2[iter2->first][iter->first] = iter2->second;
        }
    }
    for (auto iter = B3.begin(); iter != B3.end(); iter ++) {
        for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); ++iter2) {
            invB3[iter2->first][iter->first] = iter2->second;
        }
    }
    for (auto iter = B4.begin(); iter != B4.end(); iter ++) {
        for (auto iter2 = iter->second.begin(); iter2 != iter->second.end(); ++iter2) {
            invB4[iter2->first][iter->first] = iter2->second;
        }
    }
}