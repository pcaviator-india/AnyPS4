#ifndef CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNPROGRAM_HPP
#define CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNPROGRAM_HPP

#include "GcnDecoder/GcnInstruction.hpp"
#include <cstdint>
#include <vector>
#include <span>

namespace ShaderRecompiler {

struct GcnProgram {
    std::span<const std::uint32_t> code;
    std::vector<GcnInstruction> instructions;
};

[[nodiscard]] const GcnInstruction* FindInstructionAtProgramCounter(const GcnProgram& program, std::uint32_t programCounter);

} // namespace ShaderRecompiler

#endif
