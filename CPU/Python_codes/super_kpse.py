import mmh3
import pickle
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
plot_titles = {
    0: "per-source destination flow",
    1: "per-source port flow",
    2: "per-destination source flow",
    3: "per-service source flow",
    4: "per-source service flow"
}
def get_opt_k(p):
    if p <= 0.5:
        return 1
    else:
        k_low = np.floor(-np.log2(1 - p))
        k_high = np.ceil(-np.log2(1 - p))
        M_low = - k_low / (np.log(1 - (1 - p) ** (1 / k_low)))
        M_high = - k_high / (np.log(1 - (1 - p) ** (1 / k_high)))
        if M_low <= M_high:
            return int(k_low)
        else:
            return int(k_high)
def get_opt_men(p, N):
    k = get_opt_k(p)
    M = - k * N / (np.log(1 - (1 - p) ** (1 / k)))
    return int(M / 8 / 1024)

def search_for_k_p(N, M):
    pre_p = None
    pre_k = None
    for p in np.arange(0.01, 1.0, 0.01).tolist():
        k = get_opt_k(p)
        if - k * N / np.log(1 - (1 - p) ** (1 / k)) <= M:
            pre_p =  p
            pre_k = k
        else:
            return pre_p, pre_k


class MIME:
    '''
     prob: the overall sampling rate of MIME
     bits: the number of total bits in MIME
    '''

    def __init__(self, prob, bits, k):
        self.prob = prob
        self.bits = bits
        self.k = k
        self.B = np.zeros(shape=(self.bits,), dtype=np.int8)
        self.hash_seeds = set()
        while len(self.hash_seeds) != self.k:
            self.hash_seeds.add(np.random.randint(10000, 20000))
        self.hash_seeds = list(self.hash_seeds)
        self.sample_seed = np.random.randint(10000, 20000)
        self.bitcube = dict()
        self.invbitcube = dict()
        self.servicebitcube = dict()
        self.sample_nums = 0
        self.count_ones = [0 for i in range(self.k)]
        self.post_sampling_rate = prob
        self.split_num = int(round(1 / self.prob))
        self.real_spread_set_dc = defaultdict(set)
        self.real_spread_set_dpc = defaultdict(set)
        self.real_spread_set_sc = defaultdict(set)
        self.real_spread_set_service = defaultdict(set)
        self.real_spread_set_sservice = defaultdict(set)

        self.real_spreads_dc = defaultdict(int)
        self.pred_spreads_dc = defaultdict(int)
        self.real_spreads_dpc = defaultdict(int)
        self.real_spread_service = defaultdict(int)
        self.real_spread_sservice = defaultdict(int)

        self.pred_spreads_dpc = defaultdict(int)
        self.real_spreads_sc = defaultdict(int)
        self.pred_spreads_sc = defaultdict(int)
        self.pred_spreads_service = defaultdict(int)
        self.pred_spreads_sservice = defaultdict(int)

        self.are_dc = 0
        self.are_dpc = 0
        self.are_sc = 0
        self.are_service = 0
        self.are_sservice = 0

        self.dc_count = 0
        self.dpc_count = 0
        self.sc_count = 0
        self.service_count = 0
        self.sservice_count = 0

        self.are_range_dc = dict()
        self.are_range_dpc = dict()
        self.are_range_sc = dict()
        self.are_range_service = dict()
        self.are_range_sservice = dict()

        self.are_count_dc = dict()
        self.are_count_dpc = dict()
        self.are_count_sc = dict()
        self.are_count_service = dict()
        self.are_count_sservice = dict()

        for i in range(7):
            self.are_count_dc[i] = 0
            self.are_count_dpc[i] = 0
            self.are_count_sc[i] = 0
            self.are_count_service[i] = 0
            self.are_count_sservice[i] = 0

            self.are_range_dc[i] = 0
            self.are_range_dpc[i] = 0
            self.are_range_sc[i] = 0
            self.are_range_service[i] = 0
            self.are_range_sservice[i] = 0

    def sample(self, src, dst, port):
        key = src + dst + port
        flag = False
        for i in range(self.k):
            hash_idx = mmh3.hash(key, seed=self.hash_seeds[i], signed=False) % self.bits
            if self.B[hash_idx] == 0:
                self.B[hash_idx] = 1
                self.count_ones[i] += 1
                flag = True
        if flag == True:
            if mmh3.hash(key, seed=self.sample_seed, signed=False) % 0xffffffff <= self.post_sampling_rate * 0xffffffff:
                if src not in self.bitcube:
                    self.bitcube[src] = {dst: {port}}
                else:
                    if dst not in self.bitcube[src]:
                        self.bitcube[src][dst] = {port}
                    else:
                        self.bitcube[src][dst].add(port)
                self.sample_nums += 1
            x = 1.0
            for i in range(self.k):
                x *= self.count_ones[i]
            self.post_sampling_rate = self.prob / (1 - (x / ((self.bits // self.k) ** self.k)))

    def build_inv_table(self):
        for src in self.bitcube:
            for dst in self.bitcube[src]:
                if dst not in self.invbitcube:
                    self.invbitcube[dst] = {src: self.bitcube[src][dst]}
                else:
                    if src not in self.invbitcube[dst]:
                        self.invbitcube[dst][src] = self.bitcube[src][dst]

    def build_service_table(self):
        for dst in self.invbitcube:
            self.servicebitcube[dst] = dict()
            for src in self.invbitcube[dst]:
                for port in self.invbitcube[dst][src]:
                    if port not in self.servicebitcube[dst]:
                        self.servicebitcube[dst][port] = {src}
                    else:
                        self.servicebitcube[dst][port].add(src)

    def estimate(self, key, task):  # flow label：1 element label：1
        length_dict, num_dict = defaultdict(int), defaultdict(int)
        if task == 0:  # DC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for index in temp_bitarray:
                length_dict[index] = len(temp_bitarray[index])
            for index in length_dict:
                num_dict[length_dict[index]] += 1
        elif task == 1:  # DPC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for port in temp_bitarray[dst]:
                    length_dict[port] += 1
            for index in length_dict:
                num_dict[length_dict[index]] += 1
        elif task == 2:  # SC estimation
            if key not in self.invbitcube:
                return 1
            temp_bitarray = self.invbitcube[key]
            for index in temp_bitarray:
                length_dict[index] = len(temp_bitarray[index])
            for index in length_dict:
                num_dict[length_dict[index]] += 1
        estimate_val = 0.0
        for k, v in num_dict.items():
            if k <= self.split_num:
                estimate_val += v / (1 - (1 - self.prob) ** k)
            else:
                estimate_val += v / (1 - (1 - self.prob) ** (k / self.prob))
        return int(round(estimate_val))

    def estimate_per_service_flow(self, key):
        '''
            per-service flow的流标签由dst和port相结合 flow label：2 element label：1
        '''
        if key[0] not in self.servicebitcube:
            return 1
        temp_bitarray = self.servicebitcube[key[0]]
        if key[1] not in temp_bitarray:
            return 1
        else:
            return int(round(len(temp_bitarray[key[1]]) / self.prob))

    def estimate_per_source_service_flow(self, key):
        '''
            per-source service flow的流标签由源地址组成，元素标签由目的地址和目的端口组成 flow label：1 element label：2
        '''
        if key not in self.bitcube:
            return 1
        sum_bits = 0
        for ele in self.bitcube[key]:
            sum_bits += len(self.bitcube[key][ele])
        return int(round(sum_bits / self.prob))

    def run(self, filename):
        f = open(filename, 'r')
        datas = f.readlines()
        f.close()
        for pkt in tqdm(datas):
            src, dst, port = pkt.strip().split(",")
            self.real_spread_set_dc[src].add(dst)
            self.real_spread_set_dpc[src].add(port)
            self.real_spread_set_sc[dst].add(src)
            self.real_spread_set_service[dst + " " + port].add(src)
            self.real_spread_set_sservice[src].add(dst + " " + port)
            self.sample(src, dst, port)

    def save_file(self, filename1, filename2):
        f = open(filename1, 'wb')
        pickle.dump(self.real_spread_set_dc, f)
        f.close()
        f = open(filename2, 'wb')
        pickle.dump(self.bitcube, f)
        f.close()

'''
  collect function is used to collect the supercube in previous periods
'''
def collect():
    for minute in range(3):
        filename = "./datas/0{}.txt".format(minute)
        filename1 = "./real_spreads_dc/0{}.pkl".format(minute)
        filename2 = "./pred_spreads/0{}.pkl".format(minute)
        f = open(filename, 'r')
        dat = f.readlines()
        f.close()
        N = len(dat)  # 10542501
        p = 0.7
        bits = get_opt_men(p, N) * 8 * 1024
        k = get_opt_k(p)
        print(bits, " bits, ", bits / 8 / 1024, "KB.")
        mime = None
        if minute == 0:
            mime = MIME(p, bits, k)
        elif minute == 1:
            mime = MIME(p, bits, k)
        elif minute == 2:
            mime = MIME(p, bits, k)
        mime.run(filename)
        mime.save_file(filename1, filename2)

def combinations(n, k):
    def backtrack(start, combo):
        if len(combo) == k:
            result.append(combo[:])
            return
        for i in range(start, n + 1):
            combo.append(i)
            backtrack(i + 1, combo)
            combo.pop()

    result = []
    backtrack(1, [])
    return result

def combination(n, k):
    if k == 0 or k == n:
        return 1
    else:
        return combination(n - 1, k - 1) + combination(n - 1, k)


class KSuperCube:

    def __init__(self, prob, t, k):
        self.prob = prob
        self.t = t
        self.k = k
        self.real_hash_table_table_dc = {}
        self.real_hash_table_table_dpc = {}
        self.real_hash_table_table_sc = {}
        self.pred_hash_table_table_dc = {}
        self.pred_hash_table_table_dpc = {}
        self.pred_hash_table_table_sc = {}
        self.total_spreads_dc = {}
        self.total_spreads_dpc = {}
        self.total_spreads_sc = {}
        for i in range(1, t + 1):
            self.real_hash_table_table_dc[i] = None
            self.real_hash_table_table_dpc[i] = None
            self.real_hash_table_table_sc[i] = None
            self.pred_hash_table_table_dc[i] = None
            self.pred_hash_table_table_dpc[i] = None
            self.pred_hash_table_table_sc[i] = None
        self.real_spreads_dc = defaultdict(int)
        self.real_spreads_dpc = defaultdict(int)
        self.real_spreads_sc = defaultdict(int)
        self.pred_spreads_dc = defaultdict(int)
        self.pred_spreads_dpc = defaultdict(int)
        self.pred_spreads_sc = defaultdict(int)
        self.are_dc = 0.0
        self.are_dpc = 0.0
        self.are_sc = 0.0
        self.count_dc = 0
        self.count_dpc = 0
        self.count_sc = 0
        self.range_are_dc = {}
        self.range_are_dpc = {}
        self.range_are_sc = {}
        self.range_count_dc = {}
        self.range_count_dpc = {}
        self.range_count_sc = {}
        for i in range(7):
            self.range_are_dc[i] = 0.0
            self.range_are_dpc[i] = 0.0
            self.range_are_sc[i] = 0.0
            self.range_count_dc[i] = 0
            self.range_count_dpc[i] = 0
            self.range_count_sc[i] = 0

    def init_data(self, dir_dc, dir_dpc, dir_sc, dir_est):
        for idx, real_file in enumerate(['00.pkl', '01.pkl', '02.pkl']):
            if real_file.find(".pkl") == -1:
                continue
            f = open(dir_dc + real_file, 'rb')
            print(dir_dc + real_file)
            hash_table = pickle.load(f)
            self.real_hash_table_table_dc[idx + 1] = hash_table
            f.close()
        print("[Message] DC real dataset has been loaded.")
        for idx, real_file in enumerate(['00.pkl', '01.pkl', '02.pkl']):
            if real_file.find(".pkl") == -1:
                continue
            f = open(dir_dpc + real_file, 'rb')
            print(dir_dpc + real_file)
            hash_table = pickle.load(f)
            self.real_hash_table_table_dpc[idx + 1] = hash_table
            f.close()
        print("[Message] DPC real dataset has been loaded.")
        for idx, real_file in enumerate(['00.pkl', '01.pkl', '02.pkl']):
            if real_file.find(".pkl") == -1:
                continue
            f = open(dir_sc + real_file, 'rb')
            print(dir_sc + real_file)
            hash_table = pickle.load(f)
            self.real_hash_table_table_sc[idx + 1] = hash_table
            f.close()
        print("[Message] SC real dataset has been loaded.")
        for idx, pred_file in enumerate(["00.pkl", '01.pkl', '02.pkl']):
            if pred_file.find(".pkl") == -1:
                continue
            f = open(dir_est + pred_file, 'rb')
            print(dir_est + pred_file)
            hash_table = pickle.load(f)
            self.pred_hash_table_table_dc[idx + 1] = hash_table
            self.pred_hash_table_table_dpc[idx + 1] = {}
            self.pred_hash_table_table_sc[idx + 1] = {}
            for key in tqdm(hash_table):
                self.pred_hash_table_table_dpc[idx + 1][key] = {}
                for dst in hash_table[key]:
                    if dst not in self.pred_hash_table_table_sc[idx + 1]:
                        self.pred_hash_table_table_sc[idx + 1][dst] = {
                            key: self.pred_hash_table_table_dc[idx + 1][key][dst]}
                    else:
                        if key not in self.pred_hash_table_table_sc[idx + 1][dst]:
                            self.pred_hash_table_table_sc[idx + 1][dst][key] = \
                            self.pred_hash_table_table_dc[idx + 1][key][dst]
                    for port in hash_table[key][dst]:
                        if port not in self.pred_hash_table_table_dpc[idx + 1][key]:
                            self.pred_hash_table_table_dpc[idx + 1][key][port] = {dst}
                        else:
                            self.pred_hash_table_table_dpc[idx + 1][key][port].add(dst)
            f.close()
        print("[Message] Dataset has been initted.")
        for idx in tqdm(range(self.t)):
            table = self.real_hash_table_table_dc[idx + 1]
            for key in table:
                if key not in self.total_spreads_dc:
                    self.total_spreads_dc[key] = {}
                    for ele in table[key]:
                        self.total_spreads_dc[key][ele] = 1
                else:
                    for ele in table[key]:
                        if ele in self.total_spreads_dc[key]:
                            self.total_spreads_dc[key][ele] += 1
                        else:
                            self.total_spreads_dc[key][ele] = 1
        for key in tqdm(self.total_spreads_dc):
            count_ = 0
            for ele in self.total_spreads_dc[key]:
                if self.total_spreads_dc[key][ele] >= self.k:
                    count_ += 1
            self.real_spreads_dc[key] = count_
        print("[Message] DC real spreads have been finished.")
        for idx in tqdm(range(self.t)):
            table = self.real_hash_table_table_dpc[idx + 1]
            for key in table:
                if key not in self.total_spreads_dpc:
                    self.total_spreads_dpc[key] = {}
                    for ele in table[key]:
                        self.total_spreads_dpc[key][ele] = 1
                else:
                    for ele in table[key]:
                        if ele in self.total_spreads_dpc[key]:
                            self.total_spreads_dpc[key][ele] += 1
                        else:
                            self.total_spreads_dpc[key][ele] = 1
        for key in tqdm(self.total_spreads_dpc):
            count_ = 0
            for ele in self.total_spreads_dpc[key]:
                if self.total_spreads_dpc[key][ele] >= self.k:
                    count_ += 1
            self.real_spreads_dpc[key] = count_
        print("[Message] DPC real spreads have been finished.")
        for idx in tqdm(range(self.t)):
            table = self.real_hash_table_table_sc[idx + 1]
            for key in table:
                if key not in self.total_spreads_sc:
                    self.total_spreads_sc[key] = {}
                    for ele in table[key]:
                        self.total_spreads_sc[key][ele] = 1
                else:
                    for ele in table[key]:
                        if ele in self.total_spreads_sc[key]:
                            self.total_spreads_sc[key][ele] += 1
                        else:
                            self.total_spreads_sc[key][ele] = 1
        for key in tqdm(self.total_spreads_sc):
            count_ = 0
            for ele in self.total_spreads_sc[key]:
                if self.total_spreads_sc[key][ele] >= self.k:
                    count_ += 1
            self.real_spreads_sc[key] = count_
        print("[Message] SC real spreads have been finished.")

    def estimate_dc(self, key):
        est = 0
        nfjt = {}
        for j in range(self.t, self.k - 1, -1):
            sum_j = 0
            solutions = combinations(self.t, j)
            for sol in solutions:
                Nfj = None
                for kk in range(j):
                    if kk == 0:
                        if key in self.pred_hash_table_table_dc[sol[kk]]:
                            Nfj = set(self.pred_hash_table_table_dc[sol[kk]][key].keys()).copy()
                        else:
                            Nfj = set([])
                    else:
                        if key in self.pred_hash_table_table_dc[sol[kk]]:
                            Nfj = Nfj.intersection(set(self.pred_hash_table_table_dc[sol[kk]][key].keys()))
                        else:
                            Nfj = set([])
                for ke in list(Nfj):
                    prod_p = 1
                    for s in sol:
                        v = self.pred_hash_table_table_dc[s][key][ke]
                        prod_p *= 1 - (1 - self.prob) ** len(v) if len(v) < math.ceil(1 / self.prob) else 1 - (
                                    1 - self.prob) ** (len(v) / self.prob)
                    sum_j += 1 / prod_p
            if j == self.t:
                nfjt[j] = sum_j
            else:
                temp_sum = 0
                for l in range(j + 1, self.t + 1):
                    temp_sum += combination(l, j) * nfjt[l]
                nfjt[j] = sum_j - temp_sum
        for l in range(self.k, self.t + 1):
            est += nfjt[l]
        return max(est, 1)

    def estimate_dpc(self, key):
        est = 0
        nfjt = {}
        for j in range(self.t, self.k - 1, -1):
            sum_j = 0
            solutions = combinations(self.t, j)
            for sol in solutions:
                Nfj = None
                for kk in range(j):
                    if kk == 0:
                        if key in self.pred_hash_table_table_dpc[sol[kk]]:
                            Nfj = set(self.pred_hash_table_table_dpc[sol[kk]][key].keys()).copy()
                        else:
                            Nfj = set([])
                    else:
                        if key in self.pred_hash_table_table_dpc[sol[kk]]:
                            Nfj = Nfj.intersection(set(self.pred_hash_table_table_dpc[sol[kk]][key].keys()))
                        else:
                            Nfj = set([])
                for ke in list(Nfj):
                    prod_p = 1
                    for s in sol:
                        v = self.pred_hash_table_table_dpc[s][key][ke]
                        prod_p *= 1 - (1 - self.prob) ** len(v) if len(v) < math.ceil(1 / self.prob) else 1 - (
                                    1 - self.prob) ** (len(v) / self.prob)
                    sum_j += 1 / prod_p
            if j == self.t:
                nfjt[j] = sum_j
            else:
                temp_sum = 0
                for l in range(j + 1, self.t + 1):
                    temp_sum += combination(l, j) * nfjt[l]
                nfjt[j] = sum_j - temp_sum
        for l in range(self.k, self.t + 1):
            est += nfjt[l]
        return max(est, 1)

    def estimate_sc(self, key):
        est = 0
        nfjt = {}
        for j in range(self.t, self.k - 1, -1):
            sum_j = 0
            solutions = combinations(self.t, j)
            for sol in solutions:
                Nfj = None
                for kk in range(j):
                    if kk == 0:
                        if key in self.pred_hash_table_table_sc[sol[kk]]:
                            Nfj = set(self.pred_hash_table_table_sc[sol[kk]][key].keys()).copy()
                        else:
                            Nfj = set([])
                    else:
                        if key in self.pred_hash_table_table_sc[sol[kk]]:
                            Nfj = Nfj.intersection(set(self.pred_hash_table_table_sc[sol[kk]][key].keys()))
                        else:
                            Nfj = set([])
                for ke in list(Nfj):
                    prod_p = 1
                    for s in sol:
                        v = self.pred_hash_table_table_sc[s][key][ke]
                        prod_p *= 1 - (1 - self.prob) ** len(v) if len(v) < math.ceil(1 / self.prob) else 1 - (
                                    1 - self.prob) ** (len(v) / self.prob)
                    sum_j += 1 / prod_p
            if j == self.t:
                nfjt[j] = sum_j
            else:
                temp_sum = 0
                for l in range(j + 1, self.t + 1):
                    temp_sum += combination(l, j) * nfjt[l]
                nfjt[j] = sum_j - temp_sum
        for l in range(self.k, self.t + 1):
            est += nfjt[l]
        return max(est, 1)

    def run(self):
        for key in tqdm(self.real_spreads_dc):
            real_dc = self.real_spreads_dc[key]
            if real_dc != 0:
                pred_dc = self.estimate_dc(key)
                range_dc_ = int(np.log10(real_dc)) if real_dc != 0 else 0
                self.range_count_dc[range_dc_] += 1
                self.range_are_dc[range_dc_] += abs(real_dc - pred_dc) / real_dc if real_dc != 0 else 0
                self.pred_spreads_dc[key] = pred_dc
                self.count_dc += 1
                self.are_dc += abs(real_dc - pred_dc) / real_dc if real_dc != 0 else 0
            real_dpc = self.real_spreads_dpc[key]
            if real_dpc != 0:
                pred_dpc = self.estimate_dpc(key)
                range_dpc_ = int(np.log10(real_dpc)) if real_dpc != 0 else 0
                self.range_count_dpc[range_dpc_] += 1
                self.range_are_dpc[range_dpc_] += abs(real_dpc - pred_dpc) / real_dpc if real_dpc != 0 else 0
                self.pred_spreads_dpc[key] = pred_dpc
                self.count_dpc += 1
                self.are_dpc += abs(real_dpc - pred_dpc) / real_dpc if real_dpc != 0 else 0
        for key in tqdm(self.real_spreads_sc):
            real_sc = self.real_spreads_sc[key]
            if real_sc != 0:
                pred_sc = self.estimate_sc(key)
                range_sc_ = int(np.log10(real_sc)) if real_sc != 0 else 0
                self.range_count_sc[range_sc_] += 1
                self.range_are_sc[range_sc_] += abs(real_sc - pred_sc) / real_sc if real_sc != 0 else 0
                self.count_sc += 1
                self.are_sc += abs(real_sc - pred_sc) / real_sc if real_sc != 0 else 0
                self.pred_spreads_sc[key] = pred_sc
        print("[Message] K-dc, K-dpc and K-sc persistent spreads estimation has been finished.")
        for idx in self.range_are_dc:
            self.range_are_dc[idx] = self.range_are_dc[idx] / self.range_count_dc[idx] if self.range_count_dc[
                                                                                              idx] != 0 else 0
            self.range_are_dpc[idx] = self.range_are_dpc[idx] / self.range_count_dpc[idx] if self.range_count_dpc[
                                                                                                 idx] != 0 else 0
            self.range_are_sc[idx] = self.range_are_sc[idx] / self.range_count_sc[idx] if self.range_count_sc[
                                                                                              idx] != 0 else 0
        self.are_dc = self.are_dc / self.count_dc
        self.are_dpc = self.are_dpc / self.count_dpc
        self.are_sc = self.are_sc / self.count_sc

    def draw_dc(self):
        x = np.arange(0, 7, 1)
        x_log = []
        y_log = []
        for key in tqdm(self.pred_spreads_dc):
            x_log.append(self.real_spreads_dc[key])
            y_log.append(self.pred_spreads_dc[key])
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x, x, color='black')
        plt.plot(x_log, y_log, '*', color='black')
        plt.xlabel("Real Spreads")
        plt.ylabel("Estimated Spreads")
        plt.title("K persistent dc estimation")
        plt.show()

    def draw_dpc(self):
        x = np.arange(0, 7, 1)
        x_log = []
        y_log = []
        for key in tqdm(self.pred_spreads_dpc):
            x_log.append(self.real_spreads_dpc[key])
            y_log.append(self.pred_spreads_dpc[key])
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x, x, color='black')
        plt.plot(x_log, y_log, '*', color='black')
        plt.xlabel("Real Spreads")
        plt.ylabel("Estimated Spreads")
        plt.title("K persistent dpc estimation")
        plt.show()

    def draw_sc(self):
        x = np.arange(0, 7, 1)
        x_log = []
        y_log = []
        for key in tqdm(self.pred_spreads_sc):
            x_log.append(self.real_spreads_sc[key])
            y_log.append(self.pred_spreads_sc[key])
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x, x, color='black')
        plt.plot(x_log, y_log, '*', color='black')
        plt.xlabel("Real Spreads")
        plt.ylabel("Estimated Spreads")
        plt.title("K persistent sc estimation")
        plt.show()

    def show(self, filename, k):
        f = open(filename + "/DC_{}.txt".format(k), 'w')
        f.write("DC measure:\n")
        f.write(str(self.are_dc) + "\n")
        for i in range(7):
            f.write("$[10^{},10^{})$: {}\n".format(i, i + 1, self.range_are_dc[i]))
        f.close()
        f = open(filename + "/DPC_{}.txt".format(k), 'w')
        f.write("DPC measure:\n")
        f.write(str(self.are_dpc) + "\n")
        for i in range(7):
            f.write("$[10^{},10^{})$: {}\n".format(i, i + 1, self.range_are_dpc[i]))
        f.close()
        f = open(filename + "/SC_{}.txt".format(k), 'w')
        f.write("SC measure:\n")
        f.write(str(self.are_sc) + "\n")
        for i in range(7):
            f.write("$[10^{},10^{})$: {}\n".format(i, i + 1, self.range_are_sc[i]))

def output():
    p = 0.7
    t = 3
    k_lst = [2, 3]
    for k in k_lst:
        print("k = ", k)
        ksc = KSuperCube(p, t, k)
        dir_dc = "./real_spreads_dc/"
        dir_dpc = "./real_spreads_dpc/"
        dir_sc = "./real_spreads_sc/"
        dir_est = "./pred_spreads/"
        ksc.init_data(dir_dc, dir_dpc, dir_sc, dir_est)
        ksc.run()
        ksc.draw_dc()
        ksc.draw_dpc()
        ksc.draw_sc()
        path_name = "./experiments/SuperK/MIME"
        if not os.path.isdir(path_name):
            os.makedirs(path_name)
        ksc.show(path_name, k)

if __name__ == '__main__':
    output()