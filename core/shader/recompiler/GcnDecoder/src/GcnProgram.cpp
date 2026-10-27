#include "GcnDecoder/GcnProgram.hpp"

namespace ShaderRecompiler {

const GcnInstruction* FindInstructionAtProgramCounter(const GcnProgram& program, std::uint32_t programCounter) {
    for (const auto& inst : program.instructions) {
        if (inst.programCounter == programCounter) return &inst;
    }
    return nullptr;
}

} // namespace ShaderRecompiler
