#include "GcnDecoder/GcnInstructionDecoder.hpp"
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace ShaderRecompiler {

namespace {

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

} // namespace

} // namespace ShaderRecompiler

int main() {
    // Minimal PS4 GCN shader: just S_ENDPGM (0xbf810000)
    // This exercises the GCN decode → ConvertGcnToRdna path behind
    // --ps4-experimental-graphics (ShaderProfile::GCN).
    constexpr std::uint32_t Sendpgm = 0xbf810000u;
    constexpr std::array<std::uint32_t, 1> gcnCode{Sendpgm};

    ShaderRecompiler::GcnInstructionDecoder decoder;
    auto gcnProgram = decoder.Decode({gcnCode.data(), gcnCode.size()});

    if (gcnProgram.instructions.size() != 1u) throw std::runtime_error("expected exactly one decoded GCN instruction");
    if (gcnProgram.instructions[0].op != ShaderRecompiler::GcnOpcode::SEndpgm) throw std::runtime_error("expected S_ENDPGM opcode");

    auto rdna = ShaderRecompiler::ConvertGcnToRdna(gcnProgram);
    if (rdna.instructions.size() != 1u) throw std::runtime_error("expected exactly one Rdna instruction after conversion");
    if (rdna.instructions[0].op != ShaderRecompiler::RdnaOpcode::SEndpgm) throw std::runtime_error("expected Rdna S_ENDPGM opcode");

    std::cout << "ps4-gcn-shader: OK (GCN S_ENDPGM → Rdna S_ENDPGM)\n";
    return 0;
}
