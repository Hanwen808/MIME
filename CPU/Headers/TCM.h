//
// Created by lenovo on 2025/1/9.
//

#ifndef TCMSKETCH_TCM_H
#define TCMSKETCH_TCM_H
#include<math.h>
#include<string>
#include<iostream>
#include<memory.h>
#include<queue>
#include <vector>
#include "MurmurHash3.h"
#include "Sketch.h"
using namespace std;

class TCM
{
private:
    int width;
    int depth;
    int hashnum;
    int **value;
    bool usetable;
    int tablesize;
    uint32_t row_seed;
    uint32_t col_seed;
public:
	//hashTable<string>* mapTable;
    TCM(uint32_t w,uint32_t d,uint32_t h); // table size is set approximately to the node number in the graph.
    ~TCM()
    {
		for (int i=0; i<hashnum; ++i)
        {
                delete [] value[i];
        }
        delete [] value;
        //delete [] mapTable;
    }
    void update(uint32_t, uint32_t, uint32_t);
    uint32_t estimate_psd(uint32_t src);
    uint32_t estimate_psdp(uint32_t src);
    uint32_t estimate_pds(uint32_t dst);
};

#endif //TCMSKETCH_TCM_H
