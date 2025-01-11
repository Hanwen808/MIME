#ifndef GSS_H
#define GSS_H
#include<iostream>
#include<string>
#include<vector>
#include<queue>
#include<set>
#include<map>
#include<cmath>
#include<stdlib.h>
#include<bitset>
#include <cstdint>
#include<memory.h>
#include "MurmurHash3.h"
#define prime 739
#define bigger_p 1048576
#define timer 5
#define M 80000
#define Roomnum 2 // This is the parameter to controll the maximum number of rooms in a bucket.

struct basket {
    unsigned short src[Roomnum];
    unsigned short dst[Roomnum];
    short  weight[Roomnum];
    unsigned int idx; // need to change to unsigned long long if Roomnum is larger than 4.
};

struct mapnode {
    unsigned int h;
    unsigned short g;
};

struct linknode {
    unsigned int key;
    short weight;
    linknode* next;
};

class GSS {
private:
	int w;
	int r;
	int p;
	int s;
	int f;

	uint32_t hash_seed;

	basket* value;

	public:
		std::vector<linknode*> buffer;
		std::map<unsigned int, int> index;
		int n;
		int edge_num; // count the number of edges in the buffer to assist buffer size analysis. Self loop edge is not included as it does not use additional memory.
		GSS(int width, int range, int p_num, int size, int f_num);
		~GSS() {
			delete[] value;
		 }
		 void insert(uint32_t src, uint32_t dst, uint32_t dport);
		uint32_t estimate_psd(uint32_t src);
		uint32_t estimate_psdp(uint32_t src);
		uint32_t estimate_pds(uint32_t dst);
};

#endif //GSS_H
