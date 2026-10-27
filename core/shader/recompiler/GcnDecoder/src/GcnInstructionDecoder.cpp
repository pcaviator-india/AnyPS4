#include "GcnDecoder/GcnInstructionDecoder.hpp"
#include "GcnDecoder/GcnOpcode.hpp"
#include <cstring>
#include <string>
#include <utility>

namespace ShaderRecompiler {

namespace {

// GCN instruction field extraction helpers
inline constexpr std::uint32_t Field(std::uint32_t word, std::uint32_t hi, std::uint32_t lo) {
    return (word >> lo) & ((1u << (hi - lo + 1u)) - 1u);
}

inline constexpr bool Bit(std::uint32_t word, std::uint32_t pos) {
    return (word >> pos) & 1u;
}

// GCN major opcode field is at bits [31:30] for most formats
inline constexpr std::uint32_t MajorOp(std::uint32_t word) {
    return Field(word, 31, 30);
}

// Scalar register operands: S[0-105], VCC, etc.
inline GcnOperandKind ScalarRegKind(std::uint32_t reg) {
    if (reg <= 105u) return GcnOperandKind::ScalarRegister;
    if (reg == 106u) return GcnOperandKind::Vcc;
    if (reg == 107u) return GcnOperandKind::Null;
    if (reg == 108u) return GcnOperandKind::Exec;
    if (reg == 109u) return GcnOperandKind::Null;
    if (reg == 110u) return GcnOperandKind::Null;
    if (reg == 111u) return GcnOperandKind::Scc;
    return GcnOperandKind::Unknown;
}

// Vector register operands: V[0-255], etc.
inline GcnOperandKind VectorRegKind(std::uint32_t reg) {
    if (reg <= 255u) return GcnOperandKind::VectorRegister;
    return GcnOperandKind::Unknown;
}

} // namespace

GcnInstructionFamily GetGcnInstructionFamily(std::uint32_t word) {
    const auto major = MajorOp(word);
    switch (major) {
    case 0u: // SOP1 / SOPP / SMEM
        if (Bit(word, 29)) return GcnInstructionFamily::SMEM;
        if (Bit(word, 28)) return GcnInstructionFamily::SOPP;
        return GcnInstructionFamily::SOP1;
    case 1u: // SOP2 / SOPC
        if (Bit(word, 29)) return GcnInstructionFamily::SOPC;
        return GcnInstructionFamily::SOP2;
    case 2u: // VOP1 / VOP2 / VOP3 / VOPC / VINTRP
        if (Bit(word, 29)) {
            if (Bit(word, 28)) return GcnInstructionFamily::VOP3;
            return GcnInstructionFamily::VOPC;
        }
        if (Bit(word, 28)) return GcnInstructionFamily::VOP2;
        return GcnInstructionFamily::VOP1;
    case 3u: // MUBUF / MTBUF / FLAT / DS / MIMG / EXP
        if (Bit(word, 29)) {
            if (Bit(word, 28)) return GcnInstructionFamily::EXP;
            return GcnInstructionFamily::MIMG;
        }
        if (Bit(word, 28)) return GcnInstructionFamily::DS;
        if (Bit(word, 27)) return GcnInstructionFamily::FLAT;
        return GcnInstructionFamily::MUBUF;
    default:
        return GcnInstructionFamily::Unknown;
    }
}


GcnInstruction DecodeGcnInstruction(std::uint32_t programCounter, std::span<const std::uint32_t> code, std::uint32_t wordIndex) {
    const auto word = code[wordIndex];
    const auto family = GetGcnInstructionFamily(word);
    GcnInstruction inst{};
    inst.programCounter = programCounter;
    inst.family = family;
    inst.wordCount = 1;
    inst.rawWords[0] = word;

    // Real GCN SOPP instructions encode the major opcode 0xBF in bits [31:24]
    // with the SOPP opcode in [23:16]; S_ENDPGM (opcode 0x81) terminates the
    // shader and maps onto the shared Rdna terminator.
    if ((word >> 24) == 0xBFu) {
        const auto opcode = Field(word, 23, 16);
        inst.family = GcnInstructionFamily::SOPP;
        inst.opcodeId = opcode;
        inst.op = opcode == 0x81u ? GcnOpcode::SEndpgm : GcnOpcode::Invalid;
        return inst;
    }

    switch (family) {
    case GcnInstructionFamily::SOP1: {
        // SOP1 encoding: [31:30]=00, [29]=0, [28]=0, [27:24]=opcode, [23:20]=src0, [19:16]=dst
        const auto opcode = Field(word, 27, 24);
        const auto src0 = Field(word, 23, 20);
        const auto dst = Field(word, 19, 16);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.source0 = {GcnOperandKind::ScalarRegister, src0};
        inst.destination = {ScalarRegKind(dst), dst};
        inst.sourceCount = 1;
        break;
    }
    case GcnInstructionFamily::SOP2: {
        // SOP2 encoding: [31:30]=01, [29]=0, [28]=0, [27:22]=opcode, [21:18]=src1, [17:14]=src0, [13:10]=dst
        const auto opcode = Field(word, 27, 22);
        const auto src1 = Field(word, 21, 18);
        const auto src0 = Field(word, 17, 14);
        const auto dst = Field(word, 13, 10);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.source0 = {ScalarRegKind(src0), src0};
        inst.source1 = {ScalarRegKind(src1), src1};
        inst.destination = {ScalarRegKind(dst), dst};
        inst.sourceCount = 2;
        break;
    }
    case GcnInstructionFamily::SOPC: {
        // SOPC encoding: [31:30]=01, [29]=1, [28]=0, [27:22]=opcode, [21:18]=src1, [17:14]=src0
        const auto opcode = Field(word, 27, 22);
        const auto src1 = Field(word, 21, 18);
        const auto src0 = Field(word, 17, 14);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.source0 = {ScalarRegKind(src0), src0};
        inst.source1 = {ScalarRegKind(src1), src1};
        inst.sourceCount = 2;
        break;
    }
    case GcnInstructionFamily::SOPP: {
        // SOPP encoding: [31:30]=00, [29]=0, [28]=1, [27:22]=opcode, [21:0]=literal/imm
        const auto opcode = Field(word, 27, 22);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::VOP1: {
        // VOP1 encoding: [31:30]=10, [29]=0, [28]=0, [27:22]=opcode, [21:16]=dst, [14:10]=src0
        const auto opcode = Field(word, 27, 22);
        const auto dst = Field(word, 21, 16);
        const auto src0 = Field(word, 14, 10);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.source0 = {VectorRegKind(src0), src0};
        inst.destination = {VectorRegKind(dst), dst};
        inst.sourceCount = 1;
        break;
    }
    case GcnInstructionFamily::VOP2: {
        // VOP2 encoding: [31:30]=10, [29]=0, [28]=1, [27:22]=opcode, [21:16]=dst, [14:10]=src0, [9:6]=src1
        const auto opcode = Field(word, 27, 22);
        const auto dst = Field(word, 21, 16);
        const auto src0 = Field(word, 14, 10);
        const auto src1 = Field(word, 9, 6);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.source0 = {VectorRegKind(src0), src0};
        inst.source1 = {VectorRegKind(src1), src1};
        inst.destination = {VectorRegKind(dst), dst};
        inst.sourceCount = 2;
        break;
    }
    case GcnInstructionFamily::VOP3: {
        // VOP3 encoding: [31:30]=10, [29]=1, [28]=0, [27:22]=opcode, ... (8-byte instruction with literal)
        const auto opcode = Field(word, 27, 22);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        inst.wordCount = 2;
        if (wordIndex + 1 < code.size()) {
            inst.rawWords[1] = code[wordIndex + 1];
        }
        break;
    }
    case GcnInstructionFamily::VOPC: {
        // VOPC encoding: [31:30]=10, [29]=1, [28]=1, [27:22]=opcode, ...
        const auto opcode = Field(word, 27, 22);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::SMEM: {
        // SMEM encoding: [31:30]=00, [29]=1, [28]=0, [27:26]=opcode, ...
        const auto opcode = Field(word, 27, 26);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::MUBUF: {
        // MUBUF encoding: [31:30]=11, [29]=0, [28]=0, [27:24]=opcode, ...
        const auto opcode = Field(word, 27, 24);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::FLAT: {
        // FLAT encoding: [31:30]=11, [29]=0, [28]=1, [27:24]=opcode, ...
        const auto opcode = Field(word, 27, 24);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::DS: {
        // DS encoding: [31:30]=11, [29]=0, [28]=1, ...
        const auto opcode = Field(word, 27, 24);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::MIMG: {
        // MIMG encoding: [31:30]=11, [29]=1, [28]=0, ...
        const auto opcode = Field(word, 27, 24);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    case GcnInstructionFamily::EXP: {
        // EXP encoding: [31:30]=11, [29]=1, [28]=1, ...
        const auto opcode = Field(word, 27, 24);
        inst.opcodeId = opcode;
        inst.op = GcnOpcode::Invalid;
        break;
    }
    default:
        inst.unsupportedReason = "unknown instruction family";
        inst.op = GcnOpcode::Invalid;
        break;
    }

    return inst;
}



GcnProgram DecodeGcnFrontProgram(std::span<const std::uint32_t> front) {
    GcnProgram program{};
    program.code = front;
    return program;
}

void DecodeGcnProgram(std::span<const std::uint32_t> code, GcnProgram& program) {
    program.instructions.clear();
    for (std::uint32_t i = 0; i < static_cast<std::uint32_t>(code.size());) {
        const auto inst = DecodeGcnInstruction(i * 4u, code, i);
        program.instructions.push_back(inst);
        i += inst.wordCount;
    }
}

GcnOperand DecodeGcnScalarSource(std::uint32_t code, std::uint32_t programCounter) {
    GcnOperand op{};
    op.kind = GcnOperandKind::ScalarRegister;
    op.reg = code & 0xffu;
    return op;
}

GcnOperand DecodeGcnScalarDestination(std::uint32_t code, std::uint32_t programCounter) {
    GcnOperand op{};
    op.kind = GcnOperandKind::ScalarRegister;
    op.reg = code & 0xffu;
    return op;
}

GcnOperand DecodeGcnVectorGpr(std::uint32_t reg) {
    GcnOperand op{};
    op.kind = GcnOperandKind::VectorRegister;
    op.reg = reg;
    return op;
}

std::uint64_t GcnApertureSourceValue(const GcnOperand& operand) {
    return static_cast<std::uint64_t>(operand.reg);
}

void ReadGcnLiteralOperands(std::span<const std::uint32_t> code, std::uint32_t wordIndex, GcnInstruction& instruction) {
    // No literal operands in base GCN decoding
    static_cast<void>(code);
    static_cast<void>(wordIndex);
    static_cast<void>(instruction);
}

void SetGcnRawWords(GcnInstruction& instruction, std::span<const std::uint32_t> code, std::uint32_t wordIndex, std::uint32_t wordCount) {
    for (std::uint32_t i = 0; i < wordCount && wordIndex + i < code.size(); ++i) {
        instruction.rawWords[i] = code[wordIndex + i];
    }
}

void SetGcnUnsupported(GcnInstruction& instruction, GcnInstructionFamily family, std::uint32_t opcodeId, const char* reason) {
    instruction.family = family;
    instruction.opcodeId = opcodeId;
    instruction.op = GcnOpcode::Invalid;
    instruction.unsupportedReason = reason;
}

std::string GcnOperandToString(const GcnOperand& operand) {
    std::string result;
    switch (operand.kind) {
    case GcnOperandKind::ScalarRegister: result = "S" + std::to_string(operand.reg); break;
    case GcnOperandKind::VectorRegister: result = "V" + std::to_string(operand.reg); break;
    case GcnOperandKind::Vcc: result = "VCC"; break;
    case GcnOperandKind::Exec: result = "EXEC"; break;
    case GcnOperandKind::Scc: result = "SCC"; break;
    case GcnOperandKind::Null: result = "NULL"; break;
    case GcnOperandKind::M0: result = "M0"; break;
    default: result = "UNKNOWN"; break;
    }
    return result;
}

const char* GcnImageDimensionToString(GcnImageDimension dimension) {
    switch (dimension) {
    case GcnImageDimension::Dim1D: return "1D";
    case GcnImageDimension::Dim1DArray: return "1DArray";
    case GcnImageDimension::Dim2D: return "2D";
    case GcnImageDimension::Dim3D: return "3D";
    case GcnImageDimension::Dim2DArray: return "2DArray";
    case GcnImageDimension::Dim2DMsaa: return "2DMSAA";
    case GcnImageDimension::Dim2DMsaaArray: return "2DMSAAArray";
    default: return "Unknown";
    }
}

std::string GcnInstructionToString(const GcnInstruction& instruction) {
    std::string result = "PC=0x" + std::to_string(instruction.programCounter) + " op=";
    result += std::to_string(static_cast<std::uint32_t>(instruction.op));
    if (!instruction.unsupportedReason.empty()) {
        result += " [unsupported: " + std::string(instruction.unsupportedReason) + "]";
    }
    return result;
}

std::string GcnProgramToString(const GcnProgram& program) {
    std::string result;
    for (const auto& inst : program.instructions) {
        result += GcnInstructionToString(inst) + "\n";
    }
    return result;
}

const GcnInstruction* FindInstructionAtProgramCounter(const GcnProgram& program, std::uint32_t programCounter) {
    for (const auto& inst : program.instructions) {
        if (inst.programCounter == programCounter) return &inst;
    }
    return nullptr;
}

GcnProgram GcnInstructionDecoder::Decode(std::span<const std::uint32_t> code) const {
    GcnProgram program{};
    program.code = code;
    DecodeGcnProgram(code, program);
    return program;
}

} // namespace ShaderRecompiler

