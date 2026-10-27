#include "GcnDecoder/GcnInstructionDecoder.hpp"
#include "GcnDecoder/GcnOpcode.hpp"
#include "RdnaDecoder/RdnaOpcode.hpp"
#include <cstddef>

namespace ShaderRecompiler {

namespace {

RdnaOperand mapOperand(const GcnOperand& src) {
    RdnaOperand dst{};
    switch (src.kind) {
    case GcnOperandKind::ScalarRegister: dst.kind = RdnaOperandKind::ScalarRegister; break;
    case GcnOperandKind::VectorRegister: dst.kind = RdnaOperandKind::VectorRegister; break;
    case GcnOperandKind::Vcc: dst.kind = RdnaOperandKind::VccLo; break;
    case GcnOperandKind::Exec: dst.kind = RdnaOperandKind::ExecLo; break;
    case GcnOperandKind::Scc: dst.kind = RdnaOperandKind::Scc; break;
    case GcnOperandKind::Null: dst.kind = RdnaOperandKind::Null; break;
    case GcnOperandKind::M0: dst.kind = RdnaOperandKind::M0; break;
    default: dst.kind = RdnaOperandKind::Unknown; break;
    }
    dst.value = src.value;
    dst.signedVal = src.signedVal;
    dst.reg = src.reg;
    dst.omod = src.omod;
    dst.negate = src.negate;
    dst.absolute = src.absolute;
    dst.clamp = src.clamp;
    return dst;
}

} // namespace

RdnaProgram ConvertGcnToRdna(const GcnProgram& gcn) {
    RdnaProgram result{};
    result.code = gcn.code;
    result.instructions.reserve(gcn.instructions.size());
    for (const auto& gcnInst : gcn.instructions) {
        RdnaInstruction inst{};
        inst.programCounter = gcnInst.programCounter;
        inst.wordCount = gcnInst.wordCount;
        for (std::size_t i = 0; i < gcnInst.rawWords.size(); ++i)
            inst.rawWords[i] = gcnInst.rawWords[i];
        inst.family = static_cast<RdnaInstructionFamily>(static_cast<std::uint32_t>(gcnInst.family));
        inst.opcodeId = gcnInst.opcodeId;
        inst.sourceCount = gcnInst.sourceCount;
        inst.branchOffset = gcnInst.branchOffset;
        inst.memoryOffset = gcnInst.memoryOffset;
        inst.dataDwordCount = gcnInst.dataDwordCount;
        inst.clampResult = gcnInst.clampResult;
        inst.is64Bit = gcnInst.is64Bit;
        inst.exportTarget = gcnInst.exportTarget;
        inst.exportEnableMask = gcnInst.exportEnableMask;
        inst.exportIsCompressed = gcnInst.exportIsCompressed;
        inst.exportIsLast = gcnInst.exportIsLast;
        inst.imageOpcodeId = gcnInst.imageOpcodeId;
        inst.imageDmask = gcnInst.imageDmask;
        inst.imageDimension = static_cast<RdnaImageDimension>(static_cast<std::uint32_t>(gcnInst.imageDimension));
        inst.imageR128 = gcnInst.imageR128;
        inst.imageGlc = gcnInst.imageGlc;
        inst.imageSlc = gcnInst.imageSlc;
        inst.imageA16 = gcnInst.imageA16;
        inst.imageD16 = gcnInst.imageD16;
        inst.imageNsaDwordCount = gcnInst.imageNsaDwordCount;
        for (std::size_t i = 0; i < gcnInst.imageNsaVectorRegisters.size(); ++i)
            inst.imageNsaVectorRegisters[i] = gcnInst.imageNsaVectorRegisters[i];
        inst.unsupportedReason = gcnInst.unsupportedReason;

        inst.destination = mapOperand(gcnInst.destination);
        inst.source0 = mapOperand(gcnInst.source0);
        inst.source1 = mapOperand(gcnInst.source1);
        inst.source2 = mapOperand(gcnInst.source2);
        inst.source3 = mapOperand(gcnInst.source0);
        inst.destination2 = mapOperand(gcnInst.destination);

        switch (gcnInst.op) {
        case GcnOpcode::SMovB32: inst.op = RdnaOpcode::SMovB32; break;
        case GcnOpcode::SMovB64: inst.op = RdnaOpcode::SMovB64; break;
        case GcnOpcode::SMovkI32: inst.op = RdnaOpcode::SMovkI32; break;
        case GcnOpcode::SNotB32: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::SAddI32: inst.op = RdnaOpcode::SAddI32; break;
        case GcnOpcode::SAddU32: inst.op = RdnaOpcode::SAddU32; break;
        case GcnOpcode::SSubI32: inst.op = RdnaOpcode::SSubI32; break;
        case GcnOpcode::SSubU32: inst.op = RdnaOpcode::SSubU32; break;
        case GcnOpcode::SMulI32: inst.op = RdnaOpcode::SMulI32; break;
        case GcnOpcode::SAndB32: inst.op = RdnaOpcode::SAndB32; break;
        case GcnOpcode::SOrB32: inst.op = RdnaOpcode::SOrB32; break;
        case GcnOpcode::SXorB32: inst.op = RdnaOpcode::SXorB32; break;
        case GcnOpcode::SLshlB32: inst.op = RdnaOpcode::SLshlB32; break;
        case GcnOpcode::SLshrB32: inst.op = RdnaOpcode::SLshrB32; break;
        case GcnOpcode::SAshrI32: inst.op = RdnaOpcode::SAshrI32; break;
        case GcnOpcode::SBfeU32: inst.op = RdnaOpcode::SBfeU32; break;
        case GcnOpcode::SBfeI32: inst.op = RdnaOpcode::SBfeI32; break;
        case GcnOpcode::SCmpEqI32: inst.op = RdnaOpcode::SCmpEqI32; break;
        case GcnOpcode::SCmpLtI32: inst.op = RdnaOpcode::SCmpLtI32; break;
        case GcnOpcode::SCmpGtI32: inst.op = RdnaOpcode::SCmpGtI32; break;
        case GcnOpcode::SCmpEqU32: inst.op = RdnaOpcode::SCmpEqU32; break;
        case GcnOpcode::SCmpLtU32: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::SCmpGtU32: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::SCbranchScc0: inst.op = RdnaOpcode::SCbranchScc0; break;
        case GcnOpcode::SCbranchScc1: inst.op = RdnaOpcode::SCbranchScc1; break;
        case GcnOpcode::SCbranchVccz: inst.op = RdnaOpcode::SCbranchVccz; break;
        case GcnOpcode::SCbranchVccnz: inst.op = RdnaOpcode::SCbranchVccnz; break;
        case GcnOpcode::SCbranchExecz: inst.op = RdnaOpcode::SCbranchExecz; break;
        case GcnOpcode::SCbranchExecnz: inst.op = RdnaOpcode::SCbranchExecnz; break;
        case GcnOpcode::SBranch: inst.op = RdnaOpcode::SBranch; break;
        case GcnOpcode::SEndpgm: inst.op = RdnaOpcode::SEndpgm; break;
        case GcnOpcode::SNop: inst.op = RdnaOpcode::SNop; break;
        case GcnOpcode::SLoadDword: inst.op = RdnaOpcode::SLoadDword; break;
        case GcnOpcode::SLoadDwordx2: inst.op = RdnaOpcode::SLoadDwordx2; break;
        case GcnOpcode::SLoadDwordx4: inst.op = RdnaOpcode::SLoadDwordx4; break;
        case GcnOpcode::SLoadDwordx8: inst.op = RdnaOpcode::SLoadDwordx8; break;
        case GcnOpcode::SLoadDwordx16: inst.op = RdnaOpcode::SLoadDwordx16; break;
        case GcnOpcode::VMovB32: inst.op = RdnaOpcode::VMovB32; break;
        case GcnOpcode::VAddF32: inst.op = RdnaOpcode::VAddF32; break;
        case GcnOpcode::VSubF32: inst.op = RdnaOpcode::VSubF32; break;
        case GcnOpcode::VMulF32: inst.op = RdnaOpcode::VMulF32; break;
        case GcnOpcode::VMadF32: inst.op = RdnaOpcode::VMadF32; break;
        case GcnOpcode::VAddI32: inst.op = RdnaOpcode::VAddI32; break;
        case GcnOpcode::VSubI32: inst.op = RdnaOpcode::VSubI32; break;
        case GcnOpcode::VMulLoU32: inst.op = RdnaOpcode::VMulLoU32; break;
        case GcnOpcode::VMulHiU32: inst.op = RdnaOpcode::VMulHiU32; break;
        case GcnOpcode::VAndB32: inst.op = RdnaOpcode::VAndB32; break;
        case GcnOpcode::VOrB32: inst.op = RdnaOpcode::VOrB32; break;
        case GcnOpcode::VXorB32: inst.op = RdnaOpcode::VXorB32; break;
        case GcnOpcode::VCmpEqF32: inst.op = RdnaOpcode::VCmpEqF32; break;
        case GcnOpcode::VCmpLtF32: inst.op = RdnaOpcode::VCmpLtF32; break;
        case GcnOpcode::VCmpGtF32: inst.op = RdnaOpcode::VCmpGtF32; break;
        case GcnOpcode::VCndmaskB32: inst.op = RdnaOpcode::VCndmaskB32; break;
        case GcnOpcode::VCvtF32I32: inst.op = RdnaOpcode::VCvtF32I32; break;
        case GcnOpcode::VCvtI32F32: inst.op = RdnaOpcode::VCvtI32F32; break;
        case GcnOpcode::VCvtF32U32: inst.op = RdnaOpcode::VCvtF32U32; break;
        case GcnOpcode::VCvtU32F32: inst.op = RdnaOpcode::VCvtU32F32; break;
        case GcnOpcode::VCvtF32F16: inst.op = RdnaOpcode::VCvtF32F16; break;
        case GcnOpcode::VCvtF16F32: inst.op = RdnaOpcode::VCvtF16F32; break;
        case GcnOpcode::VRcpF32: inst.op = RdnaOpcode::VRcpF32; break;
        case GcnOpcode::VRsqF32: inst.op = RdnaOpcode::VRsqF32; break;
        case GcnOpcode::VSqrtF32: inst.op = RdnaOpcode::VSqrtF32; break;
        case GcnOpcode::VExpF32: inst.op = RdnaOpcode::VExpF32; break;
        case GcnOpcode::VLogF32: inst.op = RdnaOpcode::VLogF32; break;
        case GcnOpcode::VSinF32: inst.op = RdnaOpcode::VSinF32; break;
        case GcnOpcode::VCosF32: inst.op = RdnaOpcode::VCosF32; break;
        case GcnOpcode::VFloorF32: inst.op = RdnaOpcode::VFloorF32; break;
        case GcnOpcode::VCeilF32: inst.op = RdnaOpcode::VCeilF32; break;
        case GcnOpcode::VFractF32: inst.op = RdnaOpcode::VFractF32; break;
        case GcnOpcode::VMinF32: inst.op = RdnaOpcode::VMinF32; break;
        case GcnOpcode::VMaxF32: inst.op = RdnaOpcode::VMaxF32; break;
        case GcnOpcode::VMinI32: inst.op = RdnaOpcode::VMinI32; break;
        case GcnOpcode::VMaxI32: inst.op = RdnaOpcode::VMaxI32; break;
        case GcnOpcode::VReadfirstlaneB32: inst.op = RdnaOpcode::VReadfirstlaneB32; break;
        case GcnOpcode::VReadlaneB32: inst.op = RdnaOpcode::VReadlaneB32; break;
        case GcnOpcode::VWritelaneB32: inst.op = RdnaOpcode::VWritelaneB32; break;
        case GcnOpcode::BufferLoadFormatX: inst.op = RdnaOpcode::BufferLoadFormatX; break;
        case GcnOpcode::BufferLoadFormatXy: inst.op = RdnaOpcode::BufferLoadFormatXy; break;
        case GcnOpcode::BufferLoadFormatXyz: inst.op = RdnaOpcode::BufferLoadFormatXyz; break;
        case GcnOpcode::BufferLoadFormatXyzw: inst.op = RdnaOpcode::BufferLoadFormatXyzw; break;
        case GcnOpcode::BufferLoadDword: inst.op = RdnaOpcode::BufferLoadDword; break;
        case GcnOpcode::BufferLoadDwordx2: inst.op = RdnaOpcode::BufferLoadDwordx2; break;
        case GcnOpcode::BufferLoadDwordx4: inst.op = RdnaOpcode::BufferLoadDwordx4; break;
        case GcnOpcode::BufferStoreFormatX: inst.op = RdnaOpcode::BufferStoreFormatX; break;
        case GcnOpcode::BufferStoreDword: inst.op = RdnaOpcode::BufferStoreDword; break;
        case GcnOpcode::BufferStoreDwordx4: inst.op = RdnaOpcode::BufferStoreDwordx4; break;
        case GcnOpcode::FlatLoadDword: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::FlatLoadDwordx2: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::FlatLoadDwordx4: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::FlatStoreDword: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::FlatStoreDwordx2: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::FlatStoreDwordx4: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::ImageSample: inst.op = RdnaOpcode::ImageSample; break;
        case GcnOpcode::ImageSampleLz: inst.op = RdnaOpcode::ImageSampleLz; break;
        case GcnOpcode::ImageLoad: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::ImageStore: inst.op = RdnaOpcode::Invalid; break;
        case GcnOpcode::Exp: inst.op = RdnaOpcode::Exp; break;
        case GcnOpcode::SSwappcB64: inst.op = RdnaOpcode::SSwappcB64; break;
        default: inst.op = RdnaOpcode::Invalid; break;
        }

        result.instructions.push_back(inst);
    }
    return result;
}

} // namespace ShaderRecompiler
