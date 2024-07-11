#include <iostream>
#include <cstring>
#include <cstdint>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <sstream>
#include <vector>

uint32_t addr2dec(const char* addr) {
    std::string ip(addr);
    std::vector<int> items;
    std::istringstream iss(ip);
    std::string s;
    while (std::getline(iss, s, '.')) {
        items.push_back(std::stoi(s));
    }
    return (items[0] << 24) | (items[1] << 16) | (items[2] << 8) | items[3];
}

uint32_t convertIPv4ToUint32(const char* ipAddress) {
    uint32_t result = 0;
    int octet = 0;

    // 将字符串复制到一个可修改的缓冲区
    char ipCopy[16];
    std::strncpy(ipCopy, ipAddress, sizeof(ipCopy) - 1);
    ipCopy[sizeof(ipCopy) - 1] = '\0';  // 确保以空字符结尾

    // 使用 strtok 分割字符串
    char* token = std::strtok(ipCopy, ".");
    while (token != nullptr) {
        octet = std::stoi(token);
        result = (result << 8) + octet;
        token = std::strtok(nullptr, ".");
    }

    return result;
}

int main() {
    /*const char* ip = "192.168.1.1";
    uint32_t dec = addr2dec(ip);
    uint32_t dec2 = convertIPv4ToUint32(ip);
    std::cout << "Decimal representation: " << dec << " , " << dec2 << std::endl;*/
    std::unordered_map<uint32_t, std::unordered_map<uint32_t, std::unordered_set<uint32_t>>> mmap;
    mmap[0][1].insert(0);
    mmap[0][2].insert(1);
    mmap[0][1].insert(0);
    mmap[0][1].insert(1);
    std::cout << mmap.size() << ", mmap[0] is " << mmap[0].size() << " , mmap[0][1] is " << mmap[0][1].size() << std::endl;
    return 0;
}
