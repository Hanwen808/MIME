//
// Created by Hanwen on 2025/1/10.
//
#include "../Headers/GSS.h"

GSS::GSS(int width, int range, int p_num, int size, int f_num) {
	w = width;
	r = range; /* r x r mapped baskets */
	p = p_num; /*candidate buckets*/
	s = size;  /*multiple rooms*/
	f = f_num; /*finger print lenth*/
	n = 0;
	edge_num = 0;
	value = new basket[w*w];
	memset(value, 0, sizeof(basket)*w*w);
	srand(time(NULL));
	hash_seed = 1000 * rand() % 10000;
}

/*
 * src is the source IP address
 * dst is the destination IP address
 * dport is the destination port
 */
void GSS::insert(uint32_t src, uint32_t dst, uint32_t dport) {
	uint32_t hashValue1, hashValue2;
	MurmurHash3_x86_32(&src, 4, hash_seed, &hashValue1);
	MurmurHash3_x86_32(&dst, 4, hash_seed, &hashValue2);
	unsigned int tmp = std::pow(2,f)-1;
	unsigned short g1 = hashValue1 & tmp;
	if(g1 == 0)
		g1 += 1;
	unsigned int h1 = (hashValue1 >> f) % w;
	unsigned short g2 = hashValue2 & tmp;
	if(g2 == 0)
		g2 += 1;
	unsigned int h2 = (hashValue2 >> f) % w;
	unsigned int k1 = (h1<<f)+g1;
	unsigned int k2 = (h2<<f)+g2;
	int* tmp1 = new int[r];
	int* tmp2 = new int[r];
	tmp1[0] = g1;
	tmp2[0] = g2;
	for(int i = 1;i < r; i++) {
		tmp1[i] = (tmp1[i - 1] * timer + prime) % bigger_p;
		tmp2[i] = (tmp2[i - 1] * timer + prime) % bigger_p;
	}
	bool inserted = false;
	long key = g1 + g2;
	for(int i = 0; i < p; i++) {
		key = (key * timer + prime) % bigger_p;
		int index = key % (r * r);
		int index1 = index / r;
		int index2 = index % r;
		int p1 = (h1 + tmp1[index1]) % w;
		int p2 = (h2 + tmp2[index2]) % w;
		int pos = p1 * w + p2;
		for (int j = 0; j < s; j++) {
			if ( ( ((value[pos].idx>>(j<<3))&((1<<8)-1)) == (index1|(index2<<4)) ) && (value[pos].src[j]== g1) && (value[pos].dst[j] == g2) ) {
				value[pos].weight[j] += 1;
				inserted = true;
				break;
			}
			if (value[pos].src[j] == 0) {
				value[pos].idx |= ((index1 | (index2 << 4)) << (j<<3));
				value[pos].src[j] = g1;
				value[pos].dst[j] = g2;
				value[pos].weight[j] = 1;
				inserted = true;
				break;
			}
		}
		if(inserted)
			break;
	}
	if(!inserted) {
		std::map<unsigned int, int>::iterator it = index.find(k1);
		if(it != index.end()) {
			int tag = it->second;
			linknode* node = buffer[tag];
			while(true) {
				if (node->key == k2) {
					node->weight += 1;
					break;
				}
				if(node->next == NULL) {
					linknode* ins = new linknode;
					ins->key = k2;
					ins->weight = 1;
					ins->next = NULL;
					node->next = ins;
					edge_num ++;
					break;
				}
				node = node->next;
			}
		} else {
			index[k1] = n;
			n ++;
			linknode* node = new linknode;
			node->key = k1;
			node->weight = 0;
			if (k1 != k2) {
				linknode* ins = new linknode;
				ins->key = k2;
				ins->weight = 1;
				ins->next = NULL;
				node->next = ins;
				edge_num ++;
			} else {
				node->weight += 1;
				node->next = NULL;
			}
			buffer.push_back(node);
		}
	}
	delete [] tmp1;
	delete [] tmp2;
	return;
}

uint32_t GSS::estimate_psd(uint32_t src) {
	uint32_t hashValue1;
	MurmurHash3_x86_32(&src, 4, hash_seed, &hashValue1);
	int tmp=pow(2,f)-1;
	unsigned short g1 = hashValue1 & tmp;
	if(g1==0) g1+=1;
	unsigned int h1 = (hashValue1 >> f) % w;
	unsigned int k1 = (h1 << f) + g1;
	int* tmp1 = new int[r];
	tmp1[0] = g1;
	for (int i = 1; i < r; i ++) {
		tmp1[i] = (tmp1[i - 1] * timer + prime) % bigger_p;
	}
	uint32_t zero_bits = 0;
	for (int i = 0; i < r; i ++) {
		int p1 = (h1 + tmp1[i]) % w;
		for (int k = 0; k < w; k++) {
			int pos = p1 * w + k;
			for (int j = 0; j < s; ++j) {
				if ((((value[pos].idx >> ((j << 3)))&((1 << 4) - 1)) == i) && (value[pos].src[j] == g1)) {
					int tmp_g = value[pos].dst[j];
					if (tmp_g == 0) {
						zero_bits ++;
					}
				}
			}
		}
	}
	double res;
	if (zero_bits == 0) {
		res = (1.0 * w * s) * log(1.0 * w * s);
	} else {
		res = - (1.0 * w * s) * log(1.0 * zero_bits / (1.0 * w * s));
	}
	std::map<unsigned int, int>::iterator it = index.find(k1);
	if (it != index.end()) {
		int tag = it->second;
		linknode* node = buffer[tag];
		node = node->next;
		while (node != NULL) {
			res ++;
			node=node->next;
		}
	}
	delete[] tmp1;
	return static_cast<uint32_t>(res);
}

uint32_t GSS::estimate_psdp(uint32_t src) {
	uint32_t hashValue1;
	MurmurHash3_x86_32(&src, 4, hash_seed, &hashValue1);
	int tmp=pow(2,f)-1;
	unsigned short g1 = hashValue1 & tmp;
	if(g1==0) g1+=1;
	unsigned int h1 = (hashValue1 >> f) % w;
	unsigned int k1 = (h1 << f) + g1;
	int* tmp1 = new int[r];
	tmp1[0] = g1;
	for (int i = 1; i < r; i ++) {
		tmp1[i] = (tmp1[i - 1] * timer + prime) % bigger_p;
	}
	uint32_t est = 0;
	for (int i = 0; i < r; i ++) {
		int p1 = (h1 + tmp1[i]) % w;
		for (int k = 0; k < w; k++) {
			int pos = p1 * w + k;
			for (int j = 0; j < s; ++j) {
				if ((((value[pos].idx >> ((j << 3)))&((1 << 4) - 1)) == i) && (value[pos].src[j] == g1)) {
					est += value[pos].weight[j];
				}
			}
		}
	}
	std::map<unsigned int, int>::iterator it = index.find(k1);
	if (it != index.end()) {
		int tag = it->second;
		linknode* node = buffer[tag];
		node = node->next;
		while (node != NULL) {
			est += node->weight;
			node=node->next;
		}
	}
	delete[] tmp1;
	return est;
}

uint32_t GSS::estimate_pds(uint32_t dst) {
	uint32_t hashValue2;
	MurmurHash3_x86_32(&dst, 4, hash_seed, &hashValue2);
	int tmp=pow(2,f)-1;
	unsigned short g2 = hashValue2 & tmp;
	if(g2 == 0) g2 += 1;
	unsigned int h2 = (hashValue2 >> f) % w;
	unsigned int k2 = (h2 << f) + g2;
	int* tmp2 = new int[r];
	tmp2[0] = g2;
	for (int i = 1; i < r; i ++) {
		tmp2[i] = (tmp2[i - 1] * timer + prime) % bigger_p;
	}
	uint32_t zero_bits = 0;
	for (int i = 0; i < r; i ++) {
		int p2 = (h2 + tmp2[i]) % w;
		for (int k = 0; k < w; k++) {
			int pos = p2 + k * w;
			for (int j = 0; j < s; ++j) {
				if ((((value[pos].idx >> ((j << 3)+4))&((1 << 4) - 1)) == i) && (value[pos].dst[j] == g2)) {
					int tmp_g = value[pos].src[j];
					if (tmp_g == 0) {
						zero_bits ++;
					}
				}
			}
		}
	}
	double res;
	if (zero_bits == 0) {
		res = (1.0 * w * s) * log(1.0 * w * s);
	} else {
		res = - (1.0 * w * s) * log(1.0 * zero_bits / (1.0 * w * s));
	}
	/*std::map<unsigned int, int>::iterator it = index.find(k2);
	if (it != index.end()) {
		int tag = it->second;
		linknode* node = buffer[tag];
		node = node->next;
		while (node != NULL) {
			res ++;
			node=node->next;
		}
	}*/
    for (std::map<unsigned int, int>::iterator it = index.begin(); it != index.end(); ++it) {
        int tag = it->second;
        linknode* node = buffer[tag];
			node = node->next;
        while (node != NULL) {
				if(node->key == k2) {
					res ++;
					break;	
				}
				node = node->next;
			}
    }
	delete[] tmp2;
	return static_cast<uint32_t>(res);
}