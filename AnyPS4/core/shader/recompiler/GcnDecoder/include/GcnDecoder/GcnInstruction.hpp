#ifndef CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNINSTRUCTION_HPP
#define CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNINSTRUCTION_HPP

#include "GcnDecoder/GcnOpcode.hpp"
#include <array>
#include <cstdint>
#include <string_view>

namespace ShaderRecompiler {

enum class GcnInstructionFamily {
    Unknown,
    SOP1,
    SOP2,
    SOPC,
    SOPP,
    VOP1,
    VOP2,
    VOP3,
    VOPC,
    VINTRP,
    SMEM,
    MUBUF,
    MTBUF,
    FLAT,
    DS,
    MIMG,
    EXP
};

enum class GcnOperandKind {
    None,
    ScalarRegister,
    VectorRegister,
    Vcc,
    Exec,
    Scc,
    Null,
    LiteralConstant,
    IntegerInlineConstant,
    FloatInlineConstant,
    Unknown,
    M0,
    PopsExitingWaveId,
    SrcSharedBase,
    SrcSharedLimit,
    SrcPrivateBase,
    SrcPrivateLimit
};

enum class GcnImageDimension : std::uint32_t {
    Unknown,
    Dim1D,
    Dim1DArray,
    Dim2D,
    Dim3D,
    Dim2DArray,
    Dim2DMsaa,
    Dim2DMsaaArray
};

inline constexpr std::uint32_t MaxGcnInstructionRawWords = 4;
inline constexpr std::uint32_t MaxGcnImageNsaAddressComponents = 12;

struct GcnOperand {
    GcnOperandKind kind = GcnOperandKind::Unknown;
    std::uint32_t value = 0;
    std::int32_t signedVal = 0;
    std::uint32_t reg = 0;
    std::uint32_t omod = 0;
    bool negate = false;
    bool absolute = false;
    bool clamp = false;
};

struct GcnInstruction {
    GcnOpcode op = GcnOpcode::Invalid;
    std::uint32_t programCounter = 0;
    GcnOperand destination{};
    GcnOperand source0{};
    GcnOperand source1{};
    GcnOperand source2{};
    std::int32_t branchOffset = 0;
    std::uint32_t memoryOffset = 0;
    std::uint32_t dataDwordCount = 1;
    bool clampResult = false;
    bool is64Bit = false;
    std::uint32_t exportTarget = 0;
    std::uint32_t exportEnableMask = 0;
    bool exportIsCompressed = false;
    bool exportIsLast = false;
    std::uint32_t imageOpcodeId = 0;
    std::uint32_t imageDmask = 0;
    GcnImageDimension imageDimension = GcnImageDimension::Unknown;
    bool imageR128 = false;
    bool imageGlc = false;
    bool imageSlc = false;
    bool imageA16 = false;
    bool imageD16 = false;
    std::uint32_t imageNsaDwordCount = 0;
    std::array<std::uint32_t, MaxGcnImageNsaAddressComponents> imageNsaVectorRegisters{};
    std::uint32_t wordCount = 1;
    std::array<std::uint32_t, MaxGcnInstructionRawWords> rawWords{};
    GcnInstructionFamily family = GcnInstructionFamily::Unknown;
    std::uint32_t opcodeId = 0;
    std::uint32_t sourceCount = 0;
    std::string_view unsupportedReason{};
};

} // namespace ShaderRecompiler

#endif
