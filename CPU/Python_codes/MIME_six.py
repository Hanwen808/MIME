import mmh3
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import math
import time
import math
import os

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

plot_titles = {
    0: "per-source destination flow",
    1: "per-source destination port flow",
    2: "per-destination source flow",
    3: "per-destination source port flow",
    4: "per-source protocol destination flow",
    5: "per-destination protocol source flow"
}
addition_info = "_1_min_"
addition_dir = "1 min"


class MIME:
    '''
     prob: the overall sampling rate of MIME
     bits: the number of total bits in MIME
    '''

    def __init__(self, prob, bits):
        self.prob = prob
        self.bits = bits
        self.k = get_opt_k(prob)
        self.memory = self.bits / 8 / 1024
        self.B = np.zeros(shape=(self.bits,), dtype=np.int8)
        self.hash_seeds = set([])
        while len(self.hash_seeds) != self.k:
            self.hash_seeds.add(np.random.randint(10000, 20000))
        self.hash_seeds = list(self.hash_seeds)
        self.sample_seed = 97561
        self.port_seed = 91231
        self.bitcube = dict()
        self.prot_bitcube = dict()
        self.invbitcube = dict()
        self.inv_prot_bitcube = dict()
        self.sample_nums = 0
        self.count_ones = [0 for i in range(self.k)]
        self.post_sampling_rate = self.prob
        self.split_num = int(1 / self.prob)
        self.real_spread_set_dc = defaultdict(set)
        self.real_spread_set_dpc = defaultdict(set)
        self.real_spread_set_spc = defaultdict(set)
        self.real_spread_set_sc = defaultdict(set)
        self.real_spread_set_sdc = defaultdict(set)
        self.real_spread_set_esc = defaultdict(set)

        self.real_spreads_dc = defaultdict(int)
        self.real_spreads_sc = defaultdict(int)
        self.real_spreads_dpc = defaultdict(int)
        self.real_spreads_spc = defaultdict(int)
        self.real_spreads_sdc = defaultdict(int)
        self.real_spreads_esc = defaultdict(int)

        self.pred_spreads_dpc = defaultdict(int)
        self.pred_spreads_dc = defaultdict(int)
        self.pred_spreads_sc = defaultdict(int)
        self.pred_spreads_spc = defaultdict(int)
        self.pred_spreads_sdc = defaultdict(int)
        self.pred_spreads_esc = defaultdict(int)

        self.are_dc = 0
        self.are_dpc = 0
        self.are_spc = 0
        self.are_sc = 0
        self.are_sdc = 0
        self.are_esc = 0

        self.dc_count = 0
        self.dpc_count = 0
        self.spc_count = 0
        self.sc_count = 0
        self.sdc_count = 0
        self.esc_count = 0

        self.are_range_dc = dict()
        self.are_range_dpc = dict()
        self.are_range_spc = dict()
        self.are_range_sc = dict()
        self.are_range_sdc = dict()
        self.are_range_esc = dict()

        self.are_count_dc = dict()
        self.are_count_dpc = dict()
        self.are_count_spc = dict()
        self.are_count_sc = dict()
        self.are_count_sdc = dict()
        self.are_count_esc = dict()

        for i in range(7):
            self.are_count_dc[i] = 0
            self.are_count_dpc[i] = 0
            self.are_count_sc[i] = 0
            self.are_count_spc[i] = 0
            self.are_count_sdc[i] = 0
            self.are_count_esc[i] = 0

            self.are_range_dc[i] = 0
            self.are_range_dpc[i] = 0
            self.are_range_sc[i] = 0
            self.are_range_spc[i] = 0
            self.are_range_sdc[i] = 0
            self.are_range_esc[i] = 0

    def sample(self, src, dst, sport, dport, prot):
        # sport = str(mmh3.hash(sport, seed = 1, signed = False))
        # dport = str(mmh3.hash(dport, seed = 1, signed = False))
        key = src + " " + dst + " " + sport + " " + dport + " " + prot
        flag = False
        for i in range(self.k):
            hash_idx = i * (self.bits // self.k) + mmh3.hash(key, seed=self.hash_seeds[i], signed=False) % (
                        self.bits // self.k)
            if self.B[hash_idx] == 0:
                self.B[hash_idx] = 1
                self.count_ones[i] += 1
                flag = True
        if flag == True:
            if mmh3.hash(key, seed=self.sample_seed, signed=False) <= self.post_sampling_rate * 0xffffffff:
                if src not in self.bitcube:
                    self.bitcube[src] = {dst: {sport: {dport: {prot}}}}
                else:
                    if dst not in self.bitcube[src]:
                        self.bitcube[src][dst] = {sport: {dport: {prot}}}
                    else:
                        if sport not in self.bitcube[src][dst]:
                            self.bitcube[src][dst][sport] = {dport: {prot}}
                        else:
                            if dport not in self.bitcube[src][dst][sport]:
                                self.bitcube[src][dst][sport][dport] = {prot}
                            else:
                                self.bitcube[src][dst][sport][dport].add(prot)
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

    def build_sourcepoint_table(self):
        for src in self.bitcube:
            for dst in self.bitcube[src]:
                for sport in self.bitcube[src][dst]:
                    for dport in self.bitcube[src][dst][sport]:
                        for prot in self.bitcube[src][dst][sport][dport]:
                            if src not in self.prot_bitcube:
                                self.prot_bitcube[src] = {prot: {dst: {sport: {dport}}}}
                            else:
                                if prot not in self.prot_bitcube[src]:
                                    self.prot_bitcube[src][prot] = {dst: {sport: {dport}}}
                                else:
                                    if dst not in self.prot_bitcube[src][prot]:
                                        self.prot_bitcube[src][prot][dst] = {sport: {dport}}
                                    else:
                                        if sport not in self.prot_bitcube[src][prot][dst]:
                                            self.prot_bitcube[src][prot][dst][sport] = {dport}
                                        else:
                                            self.prot_bitcube[src][prot][dst][sport].add(dport)

    def build_endpoint_table(self):
        for dst in self.invbitcube:
            for src in self.invbitcube[dst]:
                for sport in self.invbitcube[dst][src]:
                    for dport in self.invbitcube[dst][src][sport]:
                        for prot in self.invbitcube[dst][src][sport][dport]:
                            if dst not in self.inv_prot_bitcube:
                                self.inv_prot_bitcube[dst] = {prot: {src: {sport: {dport}}}}
                            else:
                                if prot not in self.inv_prot_bitcube[dst]:
                                    self.inv_prot_bitcube[dst][prot] = {src: {sport: {dport}}}
                                else:
                                    if src not in self.inv_prot_bitcube[dst][prot]:
                                        self.inv_prot_bitcube[dst][prot][src] = {sport: {dport}}
                                    else:
                                        if sport not in self.inv_prot_bitcube[dst][prot][src]:
                                            self.inv_prot_bitcube[dst][prot][src][sport] = {dport}
                                        else:
                                            self.inv_prot_bitcube[dst][prot][src][sport].add(dport)

    def estimate(self, key, task):
        length_dict, num_dict = defaultdict(int), defaultdict(int)
        sum_ = 0
        if task == 0:  # DC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    for dport in temp_bitarray[dst][sport]:
                        length_dict[dst] += len(temp_bitarray[dst][sport][dport])
            for dst in length_dict:
                num_dict[length_dict[dst]] += 1
        elif task == 1:  # DPC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    for dport in temp_bitarray[dst][sport]:
                        length_dict[dport] += len(temp_bitarray[dst][sport][dport])
            for dport in length_dict:
                num_dict[length_dict[dport]] += 1
        elif task == 2:  # SC estimation
            if key not in self.invbitcube:
                return 1
            temp_bitarray = self.invbitcube[key]
            for src in temp_bitarray:
                for sport in temp_bitarray[src]:
                    for dport in temp_bitarray[src][sport]:
                        length_dict[src] += len(temp_bitarray[src][sport][dport])
            for src in length_dict:
                num_dict[length_dict[src]] += 1
        elif task == 3:  # SPC estimation
            if key not in self.invbitcube:
                return 1
            temp_bitarray = self.invbitcube[key]
            for src in temp_bitarray:
                for sport in temp_bitarray[src]:
                    for dport in temp_bitarray[src][sport]:
                        length_dict[sport] += len(temp_bitarray[src][sport][dport])
            for sport in length_dict:
                num_dict[length_dict[sport]] += 1
        elif task == 4:  # Per-source protocol destination flow spread
            if key[0] not in self.prot_bitcube or key[1] not in self.prot_bitcube[key[0]]:
                return 1
            temp_bitarray = self.prot_bitcube[key[0]][key[1]]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    length_dict[dst] += len(temp_bitarray[dst][sport])
            for dst in length_dict:
                num_dict[length_dict[dst]] += 1
        elif task == 5:  # Per-destination protocol source flow spread
            if key[0] not in self.inv_prot_bitcube or key[1] not in self.inv_prot_bitcube[key[0]]:
                return 1
            temp_bitarray = self.inv_prot_bitcube[key[0]][key[1]]
            for src in temp_bitarray:
                for sport in temp_bitarray[src]:
                    length_dict[src] += len(temp_bitarray[src][sport])
            for src in length_dict:
                num_dict[length_dict[src]] += 1

        if task in [0, 1, 2, 3, 4, 5]:
            estimate_val = 0.0
            for k, v in num_dict.items():
                if k < math.ceil(self.split_num):
                    estimate_val += v / (1 - (1 - self.prob) ** int(k))
                else:
                    estimate_val += v / (1 - (1 - self.prob) ** int(k / self.prob))
            return int(round(estimate_val))
        else:
            return int(round(sum_ / self.prob))

    def run(self, filename):
        f = open(filename, 'r')
        datas = f.readlines()
        f.close()
        N_set = set([])
        for pkt in tqdm(datas):
            src, dst, sport, dport, prot = pkt.strip().split(",")
            self.real_spread_set_dc[src].add(dst)
            self.real_spread_set_spc[dst].add(sport)
            self.real_spread_set_dpc[src].add(dport)
            self.real_spread_set_sc[dst].add(src)
            self.real_spread_set_sdc[src + " " + prot].add(dst)
            self.real_spread_set_esc[dst + " " + prot].add(src)
            self.sample(src, dst, sport, dport, prot)
            N_set.add(pkt)
        print("N is ", len(N_set))
        old_time = time.time()
        self.build_inv_table()
        print("build inv_table needs {}".format(time.time() - old_time))
        old_time = time.time()
        self.build_endpoint_table()
        print("build inv_prot_table needs {}".format(time.time() - old_time))
        old_time = time.time()
        self.build_sourcepoint_table()
        print("build prot_table needs {}".format(time.time() - old_time))
        print("Process data has been finished.")
        for src in tqdm(self.real_spread_set_dc):
            self.real_spreads_dc[src] = len(self.real_spread_set_dc[src])
            self.pred_spreads_dc[src] = self.estimate(src, 0)
        print("The estimation of Per-source destination flow has been finished.")
        for src in tqdm(self.real_spread_set_dpc):
            self.real_spreads_dpc[src] = len(self.real_spread_set_dpc[src])
            self.pred_spreads_dpc[src] = self.estimate(src, 1)
        print("The estimation of Per-source destination port flow has been finished.")
        for dst in tqdm(self.real_spread_set_sc):
            self.real_spreads_sc[dst] = len(self.real_spread_set_sc[dst])
            self.pred_spreads_sc[dst] = self.estimate(dst, 2)
        print("The estimation of Per-destination source flow has been finished.")
        for dst in tqdm(self.real_spread_set_spc):
            self.real_spreads_spc[dst] = len(self.real_spread_set_spc[dst])
            self.pred_spreads_spc[dst] = self.estimate(dst, 3)
        print("The estimation of Per-destination source port flow has been finished.")
        for src_prot in tqdm(self.real_spread_set_sdc):
            self.real_spreads_sdc[src_prot] = len(self.real_spread_set_sdc[src_prot])
            self.pred_spreads_sdc[src_prot] = self.estimate(src_prot.split(), 4)
        print("The estimation of Per-sourcepoint source flow spread has been finished.")
        for dst_prot in tqdm(self.real_spread_set_esc):
            self.real_spreads_esc[dst_prot] = len(self.real_spread_set_esc[dst_prot])
            self.pred_spreads_esc[dst_prot] = self.estimate(dst_prot.split(), 5)
        print("The estimation of Per-endpoint source flow spread has been finished.")

    def draw(self, task):
        x_log, y_log = [], []
        if task == 0:
            for src in self.real_spreads_dc:
                temp_val = abs(self.real_spreads_dc[src] - self.pred_spreads_dc[src]) / self.real_spreads_dc[src]
                self.are_dc += temp_val
                self.dc_count += 1
                self.are_count_dc[int(np.log10(self.real_spreads_dc[src]))] += 1
                self.are_range_dc[int(np.log10(self.real_spreads_dc[src]))] += temp_val
                x_log.append(self.real_spreads_dc[src])
                y_log.append(self.pred_spreads_dc[src])
            self.are_dc = self.are_dc / self.dc_count
            for k in self.are_range_dc:
                self.are_range_dc[k] = self.are_range_dc[k] / self.are_count_dc[k] if self.are_count_dc[k] != 0 else 0
        elif task == 1:
            for src in self.real_spreads_dpc:
                temp_val = abs(self.real_spreads_dpc[src] - self.pred_spreads_dpc[src]) / self.real_spreads_dpc[src]
                self.are_dpc += temp_val
                self.dpc_count += 1
                self.are_count_dpc[int(np.log10(self.real_spreads_dpc[src]))] += 1
                self.are_range_dpc[int(np.log10(self.real_spreads_dpc[src]))] += temp_val
                x_log.append(self.real_spreads_dpc[src])
                y_log.append(self.pred_spreads_dpc[src])
            self.are_dpc = self.are_dpc / self.dpc_count
            for k in self.are_range_dpc:
                self.are_range_dpc[k] = self.are_range_dpc[k] / self.are_count_dpc[k] if self.are_count_dpc[
                                                                                             k] != 0 else 0
        elif task == 2:
            for dst in self.real_spreads_sc:
                temp_val = abs(self.real_spreads_sc[dst] - self.pred_spreads_sc[dst]) / self.real_spreads_sc[dst]
                self.are_sc += temp_val
                self.sc_count += 1
                self.are_count_sc[int(np.log10(self.real_spreads_sc[dst]))] += 1
                self.are_range_sc[int(np.log10(self.real_spreads_sc[dst]))] += temp_val
                x_log.append(self.real_spreads_sc[dst])
                y_log.append(self.pred_spreads_sc[dst])
            self.are_sc = self.are_sc / self.sc_count
            for k in self.are_range_sc:
                self.are_range_sc[k] = self.are_range_sc[k] / self.are_count_sc[k] if self.are_count_sc[k] != 0 else 0
        elif task == 3:
            for dst in self.real_spreads_spc:
                temp_val = abs(self.real_spreads_spc[dst] - self.pred_spreads_spc[dst]) / self.real_spreads_spc[dst]
                self.are_spc += temp_val
                self.spc_count += 1
                self.are_count_spc[int(np.log10(self.real_spreads_spc[dst]))] += 1
                self.are_range_spc[int(np.log10(self.real_spreads_spc[dst]))] += temp_val
                x_log.append(self.real_spreads_spc[dst])
                y_log.append(self.pred_spreads_spc[dst])
            self.are_spc = self.are_spc / self.spc_count
            for k in self.are_range_spc:
                self.are_range_spc[k] = self.are_range_spc[k] / self.are_count_spc[k] if self.are_count_spc[
                                                                                             k] != 0 else 0
        elif task == 4:
            for key in self.real_spreads_sdc:
                temp_val = abs(self.real_spreads_sdc[key] - self.pred_spreads_sdc[key]) / self.real_spreads_sdc[key]
                self.are_sdc += temp_val
                self.sdc_count += 1
                self.are_count_sdc[int(np.log10(self.real_spreads_sdc[key]))] += 1
                self.are_range_sdc[int(np.log10(self.real_spreads_sdc[key]))] += temp_val
                x_log.append(self.real_spreads_sdc[key])
                y_log.append(self.pred_spreads_sdc[key])
            self.are_sdc = self.are_sdc / self.sdc_count
            for k in self.are_range_sdc:
                self.are_range_sdc[k] = self.are_range_sdc[k] / self.are_count_sdc[k] if self.are_count_sdc[
                                                                                             k] != 0 else 0
        elif task == 5:
            for key in self.real_spreads_esc:
                temp_val = abs(self.real_spreads_esc[key] - self.pred_spreads_esc[key]) / self.real_spreads_esc[key]
                self.are_esc += temp_val
                self.esc_count += 1
                self.are_count_esc[int(np.log10(self.real_spreads_esc[key]))] += 1
                self.are_range_esc[int(np.log10(self.real_spreads_esc[key]))] += temp_val
                x_log.append(self.real_spreads_esc[key])
                y_log.append(self.pred_spreads_esc[key])
            self.are_esc = self.are_esc / self.esc_count
            for k in self.are_range_esc:
                self.are_range_esc[k] = self.are_range_esc[k] / self.are_count_esc[k] if self.are_count_esc[
                                                                                             k] != 0 else 0
        x = y = np.arange(0, 7, 1)
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x_log, y_log, '*', color='black')
        plt.plot(x, y, color='black')
        if task != 6:
            plt.xlabel("Real Spreads", fontsize=20)
            plt.ylabel("Estimated Spreads", fontsize=20)
        else:
            plt.xlabel("Real Sizes", fontsize=20)
            plt.ylabel("Estimated Sizes", fontsize=20)
        plt.xticks(x, ["$10^{}$".format(i) for i in range(7)], rotation=0, fontsize=20)
        plt.yticks(y, ["$10^{}$".format(i) for i in range(7)], rotation=0, fontsize=20)
        # plt.title(plot_titles[task],fontsize = 20)
        plt.tight_layout()
        filepath = "./experiments/six/" + addition_dir + "/" + "PBF_{}KB".format(int(self.memory))
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        plt.savefig(
            filepath + "/" + plot_titles[
                task] + addition_info + ".jpg")
        plt.show()

    def show(self):
        self.total_are_dict = {
            0: self.are_dc, 1: self.are_dpc, 2: self.are_sc, 3: self.are_spc, 5: self.are_esc, 4: self.are_sdc
        }
        self.range_are_dict = {
            0: self.are_range_dc, 1: self.are_range_dpc, 2: self.are_range_sc, 3: self.are_range_spc,
            5: self.are_range_esc, 4: self.are_range_sdc
        }
        for i in range(6):
            filepath = "./experiments/six/" + addition_dir + "/" + "{}KB".format(int(self.memory))
            if not os.path.isdir(filepath):
                os.makedirs(filepath)
            filename = filepath + "/" + \
                       plot_titles[i] + addition_info + ".txt"
            f = open(filename, 'w')
            f.write("Total ARE is {:.3f}.\n".format(self.total_are_dict[i]))
            for j in range(7):
                f.write("$[10^{},10^{})$:  {:.3f}.\n".format(j, j + 1, self.range_are_dict[i][j]))
            f.close()

N = 2607413 #11405665
for m in [500]:
    p, k = search_for_k_p(N, m * 8 * 1024)
    print("The optimal sampling rate is {}".format(p))
    mime = MIME(p, m * 8 * 1024)
    mime.run("./datas/00_prot_unique.txt")
    mime.draw(0)
    mime.draw(1)
    mime.draw(2)
    mime.draw(3)
    mime.draw(4)
    mime.draw(5)
    mime.show()