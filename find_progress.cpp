#include <cstdio>
#include <cstring>
#include <fstream>
#include <vector>

int main() {
    std::ifstream f("c:/PersonalProjects/AnyPs4/AnyPS4/core/relinker/main.cpp", std::ios::binary);
    std::vector<char> data((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    data.push_back('\0');
    
    const char* needle = "ConsoleProgress";
    size_t needleLen = strlen(needle);
    size_t idx = 0;
    while ((idx = std::string(data.data()).find(needle, idx)) != std::string::npos) {
        size_t end = std::min(data.size(), idx + 80);
        std::string chunk(data.data() + idx, end - idx);
        printf("@%zu: %s\n", idx, chunk.c_str());
        idx += needleLen;
    }
    return 0;
}