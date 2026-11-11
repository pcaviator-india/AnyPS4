#ifndef CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNOPCODE_HPP
#define CORE_SHADER_RECOMPILIER_GCNDECODER_INCLUDE_GCNDECODER_GCNOPCODE_HPP

#include <cstdint>

namespace ShaderRecompiler {

enum class GcnOpcode : std::uint16_t {
    Invalid,
    // Scalar ALU (SOP1)
    SMovB32,
    SMovB64,
    SMovkI32,
    SNotB32,
    SAddI32,
    SAddU32,
    SSubI32,
    SSubU32,
    SMulI32,
    SAndB32,
    SOrB32,
    SXorB32,
    SLshlB32,
    SLshrB32,
    SAshrI32,
    SBfeU32,
    SBfeI32,
    SCmpEqI32,
    SCmpLtI32,
    SCmpGtI32,
    SCmpEqU32,
    SCmpLtU32,
    SCmpGtU32,
    // Scalar branches (SOPP / SOPC)
    SCbranchScc0,
    SCbranchScc1,
    SCbranchVccz,
    SCbranchVccnz,
    SCbranchExecz,
    SCbranchExecnz,
    SBranch,
    SEndpgm,
    SNop,
    // Scalar memory (SMEM)
    SLoadDword,
    SLoadDwordx2,
    SLoadDwordx4,
    SLoadDwordx8,
    SLoadDwordx16,
    // Vector ALU (VOP1 / VOP2)
    VMovB32,
    VAddF32,
    VSubF32,
    VMulF32,
    VMadF32,
    VAddI32,
    VSubI32,
    VMulLoU32,
    VMulHiU32,
    VAndB32,
    VOrB32,
    VXorB32,
    VCmpEqF32,
    VCmpLtF32,
    VCmpGtF32,
    VCndmaskB32,
    VCvtF32I32,
    VCvtI32F32,
    VCvtF32U32,
    VCvtU32F32,
    VCvtF32F16,
    VCvtF16F32,
    VRcpF32,
    VRsqF32,
    VSqrtF32,
    VExpF32,
    VLogF32,
    VSinF32,
    VCosF32,
    VFloorF32,
    VCeilF32,
    VFractF32,
    VMinF32,
    VMaxF32,
    VMinI32,
    VMaxI32,
    VReadfirstlaneB32,
    VReadlaneB32,
    VWritelaneB32,
    // Vector memory (MUBUF / FLAT)
    BufferLoadFormatX,
    BufferLoadFormatXy,
    BufferLoadFormatXyz,
    BufferLoadFormatXyzw,
    BufferLoadDword,
    BufferLoadDwordx2,
    BufferLoadDwordx4,
    BufferStoreFormatX,
    BufferStoreDword,
    BufferStoreDwordx4,
    FlatLoadDword,
    FlatLoadDwordx2,
    FlatLoadDwordx4,
    FlatStoreDword,
    FlatStoreDwordx2,
    FlatStoreDwordx4,
    // Image / sampler (MIMG)
    ImageSample,
    ImageSampleLz,
    ImageLoad,
    ImageStore,
    // Export (EXP)
    Exp,
    // Swappc (registration)
    SSwappcB64,
    Count
};

[[nodiscard]] bool IsScalarAluOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsVectorAluOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsBranchOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsScalarMemoryOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsVectorMemoryOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsImageOpcode(GcnOpcode opcode);
[[nodiscard]] bool IsExportOpcode(GcnOpcode opcode);

} // namespace ShaderRecompiler

#endif
