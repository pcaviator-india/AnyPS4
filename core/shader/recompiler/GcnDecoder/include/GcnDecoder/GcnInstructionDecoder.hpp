#ifndef CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNINSTRUCTIONDECODER_HPP
#define CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNINSTRUCTIONDECODER_HPP

#include "GcnDecoder/GcnProgram.hpp"
#include "RdnaDecoder/RdnaProgram.hpp"
#include <cstdint>
#include <span>
#include <string>

namespace ShaderRecompiler {

class GcnInstructionDecoder {
public:
    [[nodiscard]] GcnProgram Decode(std::span<const std::uint32_t> code) const;

private:
    [[nodiscard]] GcnInstruction decodeAt(std::span<const std::uint32_t> code, std::uint32_t wordIndex) const;
};

GcnInstructionFamily GetGcnInstructionFamily(std::uint32_t word);
GcnInstruction DecodeGcnInstruction(std::uint32_t programCounter, std::span<const std::uint32_t> code, std::uint32_t wordIndex);
GcnProgram DecodeGcnFrontProgram(std::span<const std::uint32_t> front);
void DecodeGcnProgram(std::span<const std::uint32_t> code, GcnProgram& program);
GcnOperand DecodeGcnScalarSource(std::uint32_t code, std::uint32_t programCounter);
GcnOperand DecodeGcnScalarDestination(std::uint32_t code, std::uint32_t programCounter);
GcnOperand DecodeGcnVectorGpr(std::uint32_t reg);
std::uint64_t GcnApertureSourceValue(const GcnOperand& operand);
void ReadGcnLiteralOperands(std::span<const std::uint32_t> code, std::uint32_t wordIndex, GcnInstruction& instruction);
void SetGcnRawWords(GcnInstruction& instruction, std::span<const std::uint32_t> code, std::uint32_t wordIndex, std::uint32_t wordCount);
void SetGcnUnsupported(GcnInstruction& instruction, GcnInstructionFamily family, std::uint32_t opcodeId, const char* reason);
std::string GcnOperandToString(const GcnOperand& operand);
const char* GcnImageDimensionToString(GcnImageDimension dimension);
std::string GcnInstructionToString(const GcnInstruction& instruction);
std::string GcnProgramToString(const GcnProgram& program);

// Convert a decoded GCN program into the shared RdnaProgram IR so the
// existing ControlFlow / Translation / SpirvBackend pipeline can consume it
// unchanged. GCN opcodes without an Rdna equivalent are mapped to
// RdnaOpcode::Invalid with an unsupportedReason.
[[nodiscard]] RdnaProgram ConvertGcnToRdna(const GcnProgram& gcn);

} // namespace ShaderRecompiler

#endif
