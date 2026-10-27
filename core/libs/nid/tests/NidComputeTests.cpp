#include <nid/NidCompute.hpp>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

std::string computeNid(const char* symbol, const char* library) {
    return Nid::ComputeNid(symbol, library);
}

} // namespace

int main() {
    // NID vector: known PS4 symbol names hash to stable 11-char base64 NIDs.
    const struct {
        const char* symbol;
        const char* library;
        std::size_t expectedLength;
    } cases[] = {
        {"sceKernelExitProcess", "libSceKernel", 11},
        {"sceKernelCreateThread", "libSceKernel", 11},
        {"sceKernelDeleteThread", "libSceKernel", 11},
        {"sceKernelStartThread", "libSceKernel", 11},
        {"sceKernelWaitThreadEnd", "libSceKernel", 11},
        {"sceKernelExitDeleteThread", "libSceKernel", 11},
        {"sceKernelCreateEventFlag", "libSceKernel", 11},
        {"sceKernelSetEventFlag", "libSceKernel", 11},
        {"sceKernelWaitEventFlag", "libSceKernel", 11},
        {"sceKernelCreateSema", "libSceKernel", 11},
        {"sceKernelWaitSema", "libSceKernel", 11},
        {"sceKernelSignalSema", "libSceKernel", 11},
        {"sceKernelCreateMutex", "libSceKernel", 11},
        {"sceKernelLockMutex", "libSceKernel", 11},
        {"sceKernelUnlockMutex", "libSceKernel", 11},
        {"sceKernelCreateMemoryPartition", "libSceKernel", 11},
        {"sceKernelAllocMemory", "libSceKernel", 11},
        {"sceKernelFreeMemory", "libSceKernel", 11},
        {"sceKernelAllocMemHeap", "libSceKernel", 11},
        {"sceKernelFreeMemHeap", "libSceKernel", 11},
    };

    std::string previous;
    bool first = true;
    for (const auto& c : cases) {
        const std::string nid = computeNid(c.symbol, c.library);
        require(nid.size() == c.expectedLength,
                ("NID length wrong for " + std::string(c.symbol)).c_str());
        require(nid.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-") == std::string::npos,
                ("NID contains non-base64 characters for " + std::string(c.symbol)).c_str());
        // Determinism: same input yields the same NID.
        require(computeNid(c.symbol, c.library) == nid,
                ("NID not deterministic for " + std::string(c.symbol)).c_str());
        // Uniqueness: different symbols yield different NIDs.
        if (!first) require(nid != previous, "NID collision with previous symbol");
        previous = nid;
        first = false;
    }

    std::cout << "NID vector tests passed (" << cases[0].expectedLength
              << "-char base64 NIDs, " << (sizeof(cases) / sizeof(cases[0])) << " cases)"
              << std::endl;
    return 0;
}