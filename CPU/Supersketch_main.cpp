#include <vector>
#include <fstream>
#include <sstream>
#include <cmath>
#include <algorithm>
#include <time.h>
#include <iostream>
#include <unordered_set>
#include <unordered_map>
#include "Headers/Supersketch.h"

using namespace std;

uint32_t convertIPv4ToUint32(char* ipAddress) {
    uint32_t result = 0;
    int octet = 0;
    char ipCopy[KEY_LEN];
    strncpy(ipCopy, ipAddress, sizeof(ipCopy) - 1);
    ipCopy[sizeof(ipCopy) - 1] = '\0';
    char* token = strtok(ipCopy, ".");
    while (token != nullptr) {
        octet = std::stoi(token);
        result = (result << 8) + octet;
        token = std::strtok(nullptr, ".");
    }
    return result;
}

// Updating MIME and testing the processing throughput.
void processPackets(Sketch* skt, vector<pair<pair<uint32_t, uint32_t>, uint32_t>>& dataset) {
    clock_t start = clock(); // The start time of processing packet stream
    for (int i = 0; i < dataset.size(); i++) {
        skt->update(dataset[i].first.first, dataset[i].first.second, dataset[i].second);
    }
    clock_t current = clock(); // The end time of processing packet stream
    cout << dataset.size() << " lines: have used " << ((double)current - start) / CLOCKS_PER_SEC << " seconds" << endl;
    double throughput = (dataset.size() / 1000000.0) / (((double)current - start) / CLOCKS_PER_SEC);
    cout << "throughput: " << throughput << "Mpps" << endl;
}

/*
 *  Function: Generate the dataset and real flow spreads dict.
 *  dataDir: the directory of dataset.
 *  numOfMinutes: the measurement periods.
 *  dataset: records triple (source, destination, port)
 * */
void getDataSet(string dataDir, unsigned int numOfMinutes, vector<pair<pair<uint32_t , uint32_t >, uint32_t>>& dataset,
                unordered_map<uint32_t, unordered_set<uint32_t>>& realDCFlowInfo,
                unordered_map<uint32_t, unordered_set<uint32_t>>& realSCFlowInfo,
                unordered_map<uint32_t, unordered_set<uint32_t>>& realDPCFlowInfo)
{
    char dataFileName[20]; // The filename of dataset
    uint32_t flowId;          // flow key
    uint32_t eleId;           // element key 1
    uint32_t portId;          // element key 2
    string line, source, destination, dport;
    clock_t start = clock();
    for (unsigned int i = 0; i < numOfMinutes; i++) {
        sprintf(dataFileName, "%02d.txt ", i);
        string oneDataFilePath = "./data/00.txt"; // Organize a complete filename.
        cout << oneDataFilePath << endl;
        fstream fin(oneDataFilePath);
        while (fin.is_open() && fin.peek() != EOF) {
            getline(fin, line); // each line of dataset is consist of three fields: source address, destination address and destination port
            stringstream ss(line.c_str());
            // Build a flow element
            ss >> source >> destination >> dport;
            flowId = convertIPv4ToUint32((char *) source.c_str());
            eleId = convertIPv4ToUint32((char *) destination.c_str());
            portId = std::atoi(dport.c_str());
            dataset.push_back(make_pair(make_pair(flowId, eleId), portId));
            realDCFlowInfo[flowId].insert(eleId);
            realSCFlowInfo[eleId].insert(flowId);
            realDPCFlowInfo[flowId].insert(portId);
            if (dataset.size() % 5000000 == 0) {
                clock_t current = clock();
                cout << "have added " << dataset.size() << " packets, have used " << ((double)current - start) / CLOCKS_PER_SEC << " seconds." << endl;
            }
        }
        if (!fin.is_open()) {
            cout << "dataset file " << oneDataFilePath << "closed unexpectedlly"<<endl;
            exit(-1);
        }else
            fin.close();
    }
    clock_t current = clock();
    cout << "have added " << dataset.size() << " packets, have used " << ((double)current - start) / CLOCKS_PER_SEC << " seconds" << endl;
    // count the totol number of flows and distinct elements
    // three different type spread tasks
    auto iter = realDCFlowInfo.begin();
    unsigned int totalSpread = 0;
    while (iter != realDCFlowInfo.end()) {
        totalSpread += (iter->second).size();
        iter++;
    }
    cout << "Per-source destination flow estimation: there are " << realDCFlowInfo.size() << " flows and " << totalSpread << " distinct elements" << endl;
    iter = realSCFlowInfo.begin();
    totalSpread = 0;
    while (iter != realSCFlowInfo.end()) {
        totalSpread += (iter->second).size();
        iter ++;
    }
    cout << "Per-destination source flow estimation: there are " << realSCFlowInfo.size() << " flows and " << totalSpread << " distinct elements" << endl;
    iter = realDPCFlowInfo.begin();
    totalSpread = 0;
    while (iter != realDPCFlowInfo.end()) {
        totalSpread += (iter->second).size();
        iter ++;
    }
    cout << "Per-source port flow estimation: there are " << realDPCFlowInfo.size() << " flows and " << totalSpread << " distinct elements" << endl;
}

void saveResults(string outputFilePath, Sketch* skt, unordered_map<uint32_t, unordered_set<uint32_t>>& realFlowInfo, int taskId) {
    ofstream fout;
    vector<int> realSpreads, estimatedSpreads;
    auto iter = realFlowInfo.begin();
    fout.open(outputFilePath, ios::out);
    while (fout.is_open() && iter != realFlowInfo.end()) {
        if (iter != realFlowInfo.begin())
            fout << endl;
        unsigned int realSpread = (iter->second).size();
        unsigned int estimatedSpread = skt->estimate(iter->first, taskId);
        realSpreads.push_back(realSpread);
        estimatedSpreads.push_back(estimatedSpread);
        fout << realSpread << " " << estimatedSpread;
        iter++;
    }
    if (!fout.is_open())
        cout << outputFilePath << " closed unexpectedlly";
    else
        fout.close();
    sort(realSpreads.begin(), realSpreads.end(), greater<unsigned int>());
    cout << "";
}

int main() {
    cout << "prepare the dataset" << endl;
    string dataDir = R"(./data/)";
    unsigned int numOfMinutes = 1;
    vector<pair<pair<uint32_t, uint32_t>, uint32_t>> dataset;
    unordered_map<uint32_t, unordered_set<uint32_t>> realDCFlowInfo, realSCFlowInfo, realDPCFlowInfo;
    getDataSet(dataDir, numOfMinutes, dataset, realDCFlowInfo, realSCFlowInfo, realDPCFlowInfo);
    cout << endl;
    unsigned int cubeNum = 3;
    uint32_t P[5] {40009,40013,40031,40037,40039};
    uint32_t U[5] {401, 409, 419, 421, 431};
    Supersketch* skt = new Supersketch(cubeNum, P, U);
    cout << endl;
    cout << "Start processing..." << endl;
    processPackets(skt, dataset);
    //save the result in files
    cout << endl;
    cout << "save the result in spreads.txt ..." << endl;
    string outputFilePathDC = "./result/spreads_ss_dc.txt";
    string outputFilePathDPC = "./result/spreads_ss_dpc.txt";
    string outputFilePathSC = "./result/spreads_ss_sc.txt";
    // Here, we just test estimation of destination address of each source flow
    // Change realDCFlowInfo to realSCFlowInfo can measure the source address of each destination flow, so on.
    saveResults(outputFilePathDC, skt, realDCFlowInfo, 0);
    cout << "DC has been saved." << endl;
    saveResults(outputFilePathDPC, skt, realDPCFlowInfo, 1);
    cout <<"DPC has been saved." << endl;
    skt->initInvbitcube();
    saveResults(outputFilePathSC, skt, realSCFlowInfo, 2);
    cout << "SC has been saved." << endl;
    return 0;
}