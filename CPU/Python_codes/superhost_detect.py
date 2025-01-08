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
    1: "per-source port flow",
    2: "per-destination source flow",
    3: "per-service source flow",
    4: "per-source service flow"
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

    def __init__(self, prob, bits):
        self.prob = prob
        self.k = get_opt_k(prob)
        self.bits = bits
        self.B = np.zeros(shape=(self.bits,), dtype=np.int8)
        self.hash_seeds = set([])
        while len(self.hash_seeds) != self.k:
            self.hash_seeds.add(np.random.randint(10000, 20000))
        self.hash_seeds = list(self.hash_seeds)
        self.sample_seed = 97561
        self.port_seed = 91231
        self.bitcube_dc = dict()
        self.bitcube_dpc = dict()
        self.bitcube_sc = dict()
        self.invbitcube = dict()
        self.servicebitcube = dict()
        self.sample_nums = 0
        self.count_ones = [0 for i in range(self.k)]
        self.post_sampling_rate = self.prob
        self.split_num = math.ceil(1 / self.prob)
        self.T_dc = 1000
        self.T_dpc = 1000
        self.T_sc = 1000
        '''
          detect super host
        '''
        self.dc_muls = defaultdict(int)
        self.dpc_muls = defaultdict(int)
        self.sc_muls = defaultdict(int)
        self.dc_counters = defaultdict(float)
        self.dpc_counters = defaultdict(float)
        self.sc_counters = defaultdict(float)

        self.vert_port_scanners = set([])
        self.hor_port_scanners = set([])
        self.ddos_attackers = set([])

        self.real_vert_port = set([])
        self.real_hor_port = set([])
        self.real_ddos_attackers = set([])

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

    def add_value(self, key, mul, task):
        if task == 0:
            if key not in self.dc_counters:  # 如果该流标签没有被监测，则直接加入到片下的哈希表中
                if mul < self.split_num:
                    self.dc_counters[key] = 1 / (1 - (1 - self.prob) ** mul)
                else:
                    self.dc_counters[key] = 1 / (1 - (1 - self.prob) ** (mul / self.prob))
            else:  # 如果该流标签被监测，且当前元素的重复度为1，则直接更新
                if mul == 1:
                    self.dc_counters[key] += 1 / (1 - (1 - self.prob) ** mul)
                else:  # 如果该元素的重复不是为1，则一定之前被哈希表错误的记录过，此时需要将前一个重复度计数减去，然后加上当前的重复度计数，相当于直接将两个计数的差值相加
                    pre_mul = mul - 1
                    value1 = 1 / (1 - (1 - self.prob) ** mul) if mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (mul / self.prob))
                    value2 = 1 / (1 - (1 - self.prob) ** pre_mul) if pre_mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (pre_mul / self.prob))
                    delta = value1 - value2
                    self.dc_counters[key] += delta
            if key not in self.hor_port_scanners:
                if self.dc_counters[key] >= self.T_dc:
                    self.hor_port_scanners.add(key)
            else:
                if self.dc_counters[key] < self.T_dc:
                    self.hor_port_scanners.remove(key)
        elif task == 1:
            if key not in self.dpc_counters:
                if mul < self.split_num:
                    self.dpc_counters[key] = 1 / (1 - (1 - self.prob) ** mul)
                else:
                    self.dpc_counters[key] = 1 / (1 - (1 - self.prob) ** (mul / self.prob))
            else:
                if mul == 1:
                    self.dpc_counters[key] += 1 / (1 - (1 - self.prob) ** mul)
                else:
                    pre_mul = mul - 1
                    value1 = 1 / (1 - (1 - self.prob) ** mul) if mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (mul / self.prob))
                    value2 = 1 / (1 - (1 - self.prob) ** pre_mul) if pre_mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (pre_mul / self.prob))
                    delta = value1 - value2
                    self.dpc_counters[key] += delta
                if key not in self.vert_port_scanners:
                    if self.dpc_counters[key] >= self.T_dpc:
                        self.vert_port_scanners.add(key)
                else:
                    if self.dpc_counters[key] < self.T_dpc:
                        self.vert_port_scanners.remove(key)
        elif task == 2:
            if key not in self.sc_counters:
                if mul < self.split_num:
                    self.sc_counters[key] = 1 / (1 - (1 - self.prob) ** mul)
                else:
                    self.sc_counters[key] = 1 / (1 - (1 - self.prob) ** (mul / self.prob))
            else:
                if mul == 1:
                    self.sc_counters[key] += 1 / (1 - (1 - self.prob) ** mul)
                else:
                    pre_mul = mul - 1
                    value1 = 1 / (1 - (1 - self.prob) ** mul) if mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (mul / self.prob))
                    value2 = 1 / (1 - (1 - self.prob) ** pre_mul) if pre_mul < self.split_num else 1 / (
                                1 - (1 - self.prob) ** (pre_mul / self.prob))
                    delta = value1 - value2
                    self.sc_counters[key] += delta
                if key not in self.ddos_attackers:
                    if self.sc_counters[key] >= self.T_sc:
                        self.ddos_attackers.add(key)
                else:
                    if self.sc_counters[key] < self.T_sc:
                        self.ddos_attackers.remove(key)

    def offline(self, src, dst, port):
        # 将下载到片下的无重元素保存在DC方体中
        if src not in self.bitcube_dc:
            self.bitcube_dc[src] = {dst: {port}}
            self.add_value(src, 1, 0)
        else:
            if dst not in self.bitcube_dc[src]:
                self.bitcube_dc[src][dst] = {port}
                self.add_value(src, 1, 0)
            else:
                self.bitcube_dc[src][dst].add(port)  # 考虑无重采样的性质不可能重复计数
                self.add_value(src, len(self.bitcube_dc[src][dst]), 0)
        # 将下载到片下的无重元素保存在DPC方体中
        if src not in self.bitcube_dpc:
            self.bitcube_dpc[src] = {port: {dst}}
            self.add_value(src, 1, 1)
        else:
            if port not in self.bitcube_dpc[src]:
                self.bitcube_dpc[src][port] = {dst}
                self.add_value(src, 1, 1)
            else:
                self.bitcube_dpc[src][port].add(dst)  # 考虑无重采样的性质不可能重复计数
                self.add_value(src, len(self.bitcube_dpc[src][port]), 1)
        # 将下载到片下的无重元素保存在SC方体中
        if dst not in self.bitcube_sc:
            self.bitcube_sc[dst] = {src: {port}}
            self.add_value(dst, 1, 2)
        else:
            if src not in self.bitcube_sc[dst]:
                self.bitcube_sc[dst][src] = {port}
                self.add_value(dst, 1, 2)
            else:
                self.bitcube_sc[dst][src].add(port)
                self.add_value(dst, len(self.bitcube_sc[dst][src]), 2)

    def sample(self, src, dst, port):
        key = src + dst + port
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
                self.offline(src, dst, port)
                self.sample_nums += 1
            x = 1.0
            for i in range(self.k):
                x *= self.count_ones[i]
            self.post_sampling_rate = self.prob / (1 - (x / ((self.bits // self.k) ** self.k)))

    def show_sdc(self):
        TP = len(self.hor_port_scanners.intersection(self.real_hor_port))
        FP = len(self.hor_port_scanners - self.real_hor_port)
        FN = len(self.real_hor_port - self.hor_port_scanners)
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        F1 = (2 * precision * recall) / (precision + recall)
        print("水平扫描攻击：准确率：{:.2f}， 召回率：{:.2f}，F1：{:.2f}.".format(precision, recall, F1))
        return precision, recall, F1

    def show_sdpc(self):
        TP = len(self.vert_port_scanners.intersection(self.real_vert_port))
        FP = len(self.vert_port_scanners - self.real_vert_port)
        FN = len(self.real_vert_port - self.vert_port_scanners)
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        F1 = (2 * precision * recall) / (precision + recall)
        print("垂直扫描攻击：准确率：{:.2f}， 召回率：{:.2f}，F1：{:.2f}.".format(precision, recall, F1))
        return precision, recall, F1

    def show_ssc(self):
        TP = len(self.ddos_attackers.intersection(self.real_ddos_attackers))
        FP = len(self.ddos_attackers - self.real_ddos_attackers)
        FN = len(self.real_ddos_attackers - self.ddos_attackers)
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        F1 = (2 * precision * recall) / (precision + recall)
        print("DDoS攻击：准确率：{:.2f}， 召回率：{:.2f}， F1：{:.2f}.".format(precision, recall, F1))
        return precision, recall, F1

    def build_inv_table(self):
        for src in self.bitcube_dc:
            for dst in self.bitcube_dc[src]:
                if dst not in self.invbitcube:
                    self.invbitcube[dst] = {src: self.bitcube_dc[src][dst]}
                else:
                    if src not in self.invbitcube[dst]:
                        self.invbitcube[dst][src] = self.bitcube_dc[src][dst]

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
            if key not in self.bitcube_dc:
                return 1
            temp_bitarray = self.bitcube_dc[key]
            for index in temp_bitarray:
                length_dict[index] = len(temp_bitarray[index])
            for index in length_dict:
                num_dict[length_dict[index]] += 1
        elif task == 1:  # DPC estimation
            if key not in self.bitcube_dc:
                return 1
            temp_bitarray = self.bitcube_dc[key]
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
        if key not in self.bitcube_dc:
            return 1
        sum_bits = 0
        for ele in self.bitcube_dc[key]:
            sum_bits += len(self.bitcube_dc[key][ele])
        return int(round(sum_bits / self.prob))

    def run(self, filename):
        f = open(filename, 'r')
        datas = f.readlines()
        f.close()
        for pkt in tqdm(datas):
            src, dst, port = pkt.split()
            self.real_spread_set_dc[src].add(dst)
            self.real_spread_set_dpc[src].add(port)
            self.real_spread_set_sc[dst].add(src)
            self.real_spread_set_service[dst + " " + port].add(src)
            self.real_spread_set_sservice[src].add(dst + " " + port)
            self.sample(src, dst, port)
        self.build_inv_table()
        print("Process data has been finished.")
        for src in tqdm(self.real_spread_set_dc):
            self.real_spreads_dc[src] = len(self.real_spread_set_dc[src])
            if self.real_spreads_dc[src] >= self.T_dc:
                self.real_hor_port.add(src)
            self.pred_spreads_dc[src] = self.estimate(src, 0)
        print("The estimation of DC has been finished.")
        for src in tqdm(self.real_spread_set_dpc):
            self.real_spreads_dpc[src] = len(self.real_spread_set_dpc[src])
            if self.real_spreads_dpc[src] >= self.T_dpc:
                self.real_vert_port.add(src)
            self.pred_spreads_dpc[src] = self.estimate(src, 1)
        print("The estimation of DPC has been finished.")
        for dst in tqdm(self.real_spread_set_sc):
            self.real_spreads_sc[dst] = len(self.real_spread_set_sc[dst])
            if self.real_spreads_sc[dst] >= self.T_sc:
                self.real_ddos_attackers.add(dst)
            self.pred_spreads_sc[dst] = self.estimate(dst, 2)
        print("The estimation of SC has been finished.")
        '''
        self.build_service_table()
        for key in tqdm(self.real_spread_set_service):
            self.real_spread_service[key] = len(self.real_spread_set_service[key])
            self.pred_spreads_service[key] = self.estimate_per_service_flow(key.split())
        print("The estimation of Per-service source flow has been finished.")
        for key in tqdm(self.real_spread_set_sservice):
            self.real_spread_sservice[key] = len(self.real_spread_set_sservice[key])
            self.pred_spreads_sservice[key] = self.estimate_per_source_service_flow(key)
        print("The estimation of Per-source service flow has been finished.")
        '''

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
        elif task == 4:
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
        x = y = np.arange(0, 7, 1)
        x_log = np.log10(x_log)
        y_log = np.log10(y_log)
        plt.plot(x_log, y_log, '*')
        plt.plot(x, y)
        plt.xlabel("Real Spreads")
        plt.ylabel("Estimated Spreads")
        plt.xticks(x, ["$10^{}$".format(i) for i in range(7)])
        plt.yticks(y, ["$10^{}$".format(i) for i in range(7)])
        plt.title(plot_titles[task])
        #plt.savefig(plot_titles[task] + ".jpg")
        plt.show()

    def show(self):
        print("ARE of DC")
        print(self.are_dc)
        print(self.are_range_dc)
        print("ARE of DPC")
        print(self.are_dpc)
        print(self.are_range_dpc)
        print("ARE of SC")
        print(self.are_sc)
        print(self.are_range_sc)
        print("ARE of Per-service Source Flow")
        print(self.are_service)
        print(self.are_range_service)
        print("ARE of Per-source Service Flow")
        print(self.are_sservice)
        print(self.are_range_sservice)

if __name__ == '__main__':
    N = 2431002  # 10542501 #2431002
    filename = "./datas/00.txt"
    memory_lst = [x for x in [100, 300, 500, 700, 900]]
    filepath = "./experiments/SuperHost/Supercube/" + addition_dir
    if not os.path.isdir(filepath):
        os.makedirs(filepath)
    filename1 = "./experiments/SuperHost/Supercube/" + addition_dir + "/horizental_1000.txt"
    filename2 = "./experiments/SuperHost/Supercube/" + addition_dir + "/vertical_1000.txt"
    filename3 = "./experiments/SuperHost/Supercube/" + addition_dir + "/ddos_1000.txt"
    f1 = open(filename1, 'w')
    f2 = open(filename2, 'w')
    f3 = open(filename3, 'w')
    for m in memory_lst:
        p, k = search_for_k_p(N, m * 1024 * 8)
        print(m, p, k)
        mime = MIME(p, m * 1024 * 8)
        mime.run(filename)
        precision, recall, F1 = mime.show_sdc()
        f1.write("Memory is {}, P = {:.2f}, R = {:.2f}, F1 = {:.2f}.\n".format(m, precision, recall, F1))
        precision, recall, F1 = mime.show_sdpc()
        f2.write("Memory is {}, P = {:.2f}, R = {:.2f}, F1 = {:.2f}.\n".format(m, precision, recall, F1))
        precision, recall, F1 = mime.show_ssc()
        f3.write("Memory is {}, P = {:.2f}, R = {:.2f}, F1 = {:.2f}.\n".format(m, precision, recall, F1))
    f1.close()
    f2.close()
    f3.close()