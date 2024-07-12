//
// Created by Hanwen on 2023/11/29.
//
#include "./bitmap.h"

int countzerobits(bitmap bmp, int from, int to) {
    int z = 0;
    for (int i = from; i < to; ++i) {
        if (!getbit(i, bmp))
            z ++;
    }
    return z;
}