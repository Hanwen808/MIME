import mmh3
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

plot_titles = {
    0: "per-source destination flow",
    1: "per-source destination port flow",
    2: "per-destination source flow",
    3: "per-destination source port flow",
    4: "per-service source flow",
    5: "per-source service flow",
    6: "Original destination flow"
}
addition_info = "_1_min_"
addition_dir = "1 min"
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

def get_opt_men(p, N):
    k = get_opt_k(p)
    M = - k * N / (np.log(1 - (1 - p) ** (1 / k)))
    return int(M / 8 / 1024)


class MIME:
    '''
     prob: the overall sampling rate of MIME
     bits: the number of total bits in MIME
    '''

    def __init__(self, prob, bits):
        self.prob = prob
        self.bits = bits
        self.k = get_opt_k(prob)
        print("optimal k is ", self.k)
        self.memory = self.bits / 8 / 1024
        self.B = np.zeros(shape=(self.bits,), dtype=np.int8)
        self.hash_seeds = set([])
        while len(self.hash_seeds) != self.k:
            self.hash_seeds.add(np.random.randint(10000, 20000))
        self.hash_seeds = list(self.hash_seeds)
        self.sample_seed = 97561
        self.port_seed = 91231
        self.bitcube = dict()
        self.invbitcube = dict()
        self.servicebitcube = dict()
        self.sample_nums = 0
        self.count_ones = [0 for i in range(self.k)]
        self.post_sampling_rate = self.prob
        self.split_num = int(1 / self.prob)
        self.real_size_dc = defaultdict(int)
        self.real_spread_set_dc = defaultdict(set)
        self.real_spread_set_dpc = defaultdict(set)
        self.real_spread_set_spc = defaultdict(set)
        self.real_spread_set_sc = defaultdict(set)
        self.real_spread_set_service = defaultdict(set)
        self.real_spread_set_sservice = defaultdict(set)
        self.real_spread_set_OD = defaultdict(set)

        self.real_spreads_dc = defaultdict(int)
        self.real_spreads_sc = defaultdict(int)
        self.real_spreads_dpc = defaultdict(int)
        self.real_spreads_spc = defaultdict(int)
        self.real_spread_service = defaultdict(int)
        self.real_spread_sservice = defaultdict(int)
        self.real_spread_OD = defaultdict(int)

        self.pred_spreads_dpc = defaultdict(int)
        self.pred_spreads_dc = defaultdict(int)
        self.pred_spreads_sc = defaultdict(int)
        self.pred_spreads_spc = defaultdict(int)
        self.pred_spreads_service = defaultdict(int)
        self.pred_spreads_sservice = defaultdict(int)
        self.pred_spreads_OD = defaultdict(int)

        self.are_dc = 0
        self.are_dpc = 0
        self.are_spc = 0
        self.are_sc = 0
        self.are_service = 0
        self.are_sservice = 0
        self.are_OD = 0

        self.dc_count = 0
        self.dpc_count = 0
        self.spc_count = 0
        self.sc_count = 0
        self.service_count = 0
        self.sservice_count = 0
        self.OD_count = 0

        self.are_range_dc = dict()
        self.are_range_dpc = dict()
        self.are_range_spc = dict()
        self.are_range_sc = dict()
        self.are_range_service = dict()
        self.are_range_sservice = dict()
        self.are_range_OD = dict()

        self.are_count_dc = dict()
        self.are_count_dpc = dict()
        self.are_count_spc = dict()
        self.are_count_sc = dict()
        self.are_count_service = dict()
        self.are_count_sservice = dict()
        self.are_count_OD = dict()

        for i in range(7):
            self.are_count_dc[i] = 0
            self.are_count_dpc[i] = 0
            self.are_count_sc[i] = 0
            self.are_count_spc[i] = 0
            self.are_count_service[i] = 0
            self.are_count_sservice[i] = 0
            self.are_count_OD[i] = 0

            self.are_range_dc[i] = 0
            self.are_range_dpc[i] = 0
            self.are_range_sc[i] = 0
            self.are_range_spc[i] = 0
            self.are_range_service[i] = 0
            self.are_range_sservice[i] = 0
            self.are_range_OD[i] = 0

    def sample(self, src, dst, sport, dport):
        # sport = str(mmh3.hash(sport, seed = 1, signed = False))
        # dport = str(mmh3.hash(dport, seed = 1, signed = False))
        key = src + dst + sport + dport
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
                    self.bitcube[src] = {dst: {sport: {dport}}}
                else:
                    if dst not in self.bitcube[src]:
                        self.bitcube[src][dst] = {sport: {dport}}
                    else:
                        if sport not in self.bitcube[src][dst]:
                            self.bitcube[src][dst][sport] = {dport}
                        else:
                            self.bitcube[src][dst][sport].add(dport)
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

    def build_service_table(self):  # 类似与魔方
        for dst in self.invbitcube:
            self.servicebitcube[dst] = dict()
            for src in self.invbitcube[dst]:
                for sport in self.invbitcube[dst][src]:
                    for dport in self.invbitcube[dst][src][sport]:
                        if dport not in self.servicebitcube[dst]:
                            self.servicebitcube[dst][dport] = {src: {sport}}
                        else:
                            if src not in self.servicebitcube[dst][dport]:
                                self.servicebitcube[dst][dport][src] = {sport}
                            else:
                                self.servicebitcube[dst][dport][src].add(sport)

    def estimate(self, key, task):
        length_dict, num_dict = defaultdict(int), defaultdict(int)
        sum_ = 0
        if task == 0:  # DC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    length_dict[dst] += len(temp_bitarray[dst][sport])
            for dst in length_dict:
                num_dict[length_dict[dst]] += 1
        elif task == 1:  # DPC estimation
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    for dport in temp_bitarray[dst][sport]:
                        length_dict[dport] += 1
            for dport in length_dict:
                num_dict[length_dict[dport]] += 1
        elif task == 2:  # SC estimation
            if key not in self.invbitcube:
                return 1
            temp_bitarray = self.invbitcube[key]
            for src in temp_bitarray:
                for sport in temp_bitarray[src]:
                    length_dict[src] += len(temp_bitarray[src][sport])
            for src in length_dict:
                num_dict[length_dict[src]] += 1
        elif task == 3:  # SPC estimation
            if key not in self.invbitcube:
                return 1
            temp_bitarray = self.invbitcube[key]
            for src in temp_bitarray:
                for sport in temp_bitarray[src]:
                    length_dict[sport] += len(temp_bitarray[src][sport])
            for sport in length_dict:
                num_dict[length_dict[sport]] += 1
        elif task == 4:  # Per-service source flow
            if key[0] not in self.servicebitcube or key[1] not in self.servicebitcube[key[0]]:
                return 1
            temp_bitarray = self.servicebitcube[key[0]][key[1]]
            for src in temp_bitarray:
                length_dict[src] = len(temp_bitarray[src])
            for src in length_dict:
                num_dict[length_dict[src]] += 1
        elif task == 5:  # Per-source service flow
            if key not in self.bitcube:
                return 1
            temp_bitarray = self.bitcube[key]
            for dst in temp_bitarray:
                for sport in temp_bitarray[dst]:
                    for dport in temp_bitarray[dst][sport]:
                        length_dict[dst + " " + dport] += 1
            for key2 in length_dict:
                num_dict[length_dict[key2]] += 1
        elif task == 6:  # Original destination flow
            if key[0] not in self.bitcube or key[1] not in self.bitcube[key[0]]:
                return 1
            temp_bitarray = self.bitcube[key[0]][key[1]]
            for idx in temp_bitarray:
                sum_ += len(temp_bitarray[idx])

        if task in [0, 1, 2, 3, 4, 5]:
            estimate_val = 0.0
            for k, v in num_dict.items():
                if k < math.ceil(self.split_num):
                    estimate_val += v / (1 - (1 - self.prob) ** k)
                else:
                    estimate_val += v / (1 - (1 - self.prob) ** int(k / self.prob))
            return int(round(estimate_val))
        else:
            return int(round(sum_ / self.prob))

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
            src, dst, sport, dport = pkt.strip().split(",")
            self.real_size_dc[src] += 1
            self.real_spread_set_dc[src].add(dst)
            self.real_spread_set_spc[dst].add(sport)
            self.real_spread_set_dpc[src].add(dport)
            self.real_spread_set_sc[dst].add(src)
            self.real_spread_set_service[dst + " " + dport].add(src)
            self.real_spread_set_sservice[src].add(dst + " " + dport)
            self.real_spread_set_OD[src + " " + dst].add(sport + " " + dport)
            self.sample(src, dst, sport, dport)

        self.build_inv_table()
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

        self.build_service_table()

        for key in tqdm(self.real_spread_set_service):
            self.real_spread_service[key] = len(self.real_spread_set_service[key])
            self.pred_spreads_service[key] = self.estimate(key.split(), 4)
        print("The estimation of Per-service source flow has been finished.")
        for key in tqdm(self.real_spread_set_sservice):
            self.real_spread_sservice[key] = len(self.real_spread_set_sservice[key])
            self.pred_spreads_sservice[key] = self.estimate(key, 5)
        print("The estimation of Per-source service flow has been finished.")

        for key in tqdm(self.real_spread_set_OD):
            self.real_spread_OD[key] = len(self.real_spread_set_OD[key])
            self.pred_spreads_OD[key] = self.estimate(key.split(), 6)
        print("The estimation of Original destination flow has been finished.")

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
            for key in self.real_spread_service:
                temp_val = abs(self.real_spread_service[key] - self.pred_spreads_service[key]) / \
                           self.real_spread_service[key]
                self.are_service += temp_val
                self.service_count += 1
                self.are_count_service[int(np.log10(self.real_spread_service[key]))] += 1
                self.are_range_service[int(np.log10(self.real_spread_service[key]))] += temp_val
                x_log.append(self.real_spread_service[key])
                y_log.append(self.pred_spreads_service[key])
            self.are_service = self.are_service / self.service_count
            for k in self.are_range_service:
                self.are_range_service[k] = self.are_range_service[k] / self.are_count_service[k] if \
                self.are_count_service[k] != 0 else 0
        elif task == 5:
            for key in self.real_spread_sservice:
                temp_val = abs(self.real_spread_sservice[key] - self.pred_spreads_sservice[key]) / \
                           self.real_spread_sservice[key]
                self.are_sservice += temp_val
                self.sservice_count += 1
                self.are_count_sservice[int(np.log10(self.real_spread_sservice[key]))] += 1
                self.are_range_sservice[int(np.log10(self.real_spread_sservice[key]))] += temp_val
                x_log.append(self.real_spread_sservice[key])
                y_log.append(self.pred_spreads_sservice[key])
            self.are_sservice = self.are_sservice / self.sservice_count
            for k in self.are_range_sservice:
                self.are_range_sservice[k] = self.are_range_sservice[k] / self.are_count_sservice[k] if \
                self.are_count_sservice[k] != 0 else 0
        elif task == 6:
            for key in self.real_spread_OD:
                temp_val = abs(self.real_spread_OD[key] - self.pred_spreads_OD[key]) / self.real_spread_OD[key]
                self.are_OD += temp_val
                self.OD_count += 1
                self.are_count_OD[int(np.log10(self.real_spread_OD[key]))] += 1
                self.are_range_OD[int(np.log10(self.real_spread_OD[key]))] += temp_val
                x_log.append(self.real_spread_OD[key])
                y_log.append(self.pred_spreads_OD[key])
            self.are_OD = self.are_OD / self.OD_count
            for k in self.are_range_OD:
                self.are_range_OD[k] = self.are_range_OD[k] / self.are_count_OD[k] if self.are_count_OD[k] != 0 else 0
        x = y = np.arange(0, 7, 1)
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x_log, y_log, '*', color='black')
        plt.plot(x, y, color='black')
        plt.xlabel("Real Spreads", fontsize=20)
        plt.ylabel("Estimated Spreads", fontsize=20)
        plt.xticks(x, ["$10^{}$".format(i) for i in range(7)], rotation=0, fontsize=20)
        plt.yticks(y, ["$10^{}$".format(i) for i in range(7)], rotation=0, fontsize=20)
        # plt.title(plot_titles[task],fontsize = 20)
        plt.tight_layout()
        filepath = "./experiments/four/" + addition_dir + "/" + "PBF_{}KB".format(int(self.memory))
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        plt.savefig(
            filepath + "/" + plot_titles[
                task] + addition_info + ".jpg")
        plt.show()

    def show(self):
        self.total_are_dict = {
            0: self.are_dc, 1: self.are_dpc, 2: self.are_sc, 3: self.are_spc, 4: self.are_service, 5: self.are_sservice,
            6: self.are_OD
        }
        self.range_are_dict = {
            0: self.are_range_dc, 1: self.are_range_dpc, 2: self.are_range_sc, 3: self.are_range_spc,
            4: self.are_range_service, 5: self.are_range_sservice, 6: self.are_range_OD
        }
        for i in range(7):
            filepath = "./experiments/four/" + addition_dir + "/" + "{}KB".format(int(self.memory))
            if not os.path.isdir(filepath):
                os.makedirs(filepath)
            filename = filepath + "/" + \
                       plot_titles[i] + addition_info + ".txt"
            f = open(filename, 'w')
            f.write("Total ARE is {:.3f}.\n".format(self.total_are_dict[i]))
            for j in range(7):
                f.write("$[10^{},10^{})$:  {:.3f}.\n".format(j, j + 1, self.range_are_dict[i][j]))
            f.close()



if __name__ == '__main__':
    N = 2607408  # 11405665. 2607408 is the number of distinct stream items in one minute trace, 11405665 is the number of distinct stream items in five minute trace
    for m in [300, 500, 700, 900]:
        p, k = search_for_k_p(N, m * 8 * 1024)  # get_opt_sampling_rates(N, m * 8 * 1024)
        print("The optimal sampling rate is {}， optimal k is {}".format(p, k))
    for m in [300]:
        p, k = search_for_k_p(N, m * 8 * 1024)  # get_opt_sampling_rates(N, m * 8 * 1024)
        print("The optimal sampling rate is {}".format(p))
        mime = MIME(p, m * 8 * 1024)
        mime.run("./datas/00.txt")
        print(mime.sample_nums)
        mime.draw(0)
        mime.draw(1)
        mime.draw(2)
        mime.draw(3)
        mime.draw(4)
        mime.draw(5)
        mime.draw(6)
        mime.show()