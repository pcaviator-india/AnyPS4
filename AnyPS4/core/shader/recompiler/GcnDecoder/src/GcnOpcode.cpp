#include "GcnDecoder/GcnOpcode.hpp"

namespace ShaderRecompiler {

bool IsScalarAluOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::SMovB32:
    case GcnOpcode::SMovB64:
    case GcnOpcode::SMovkI32:
    case GcnOpcode::SNotB32:
    case GcnOpcode::SAddI32:
    case GcnOpcode::SAddU32:
    case GcnOpcode::SSubI32:
    case GcnOpcode::SSubU32:
    case GcnOpcode::SMulI32:
    case GcnOpcode::SAndB32:
    case GcnOpcode::SOrB32:
    case GcnOpcode::SXorB32:
    case GcnOpcode::SLshlB32:
    case GcnOpcode::SLshrB32:
    case GcnOpcode::SAshrI32:
    case GcnOpcode::SBfeU32:
    case GcnOpcode::SBfeI32:
    case GcnOpcode::SCmpEqI32:
    case GcnOpcode::SCmpLtI32:
    case GcnOpcode::SCmpGtI32:
    case GcnOpcode::SCmpEqU32:
    case GcnOpcode::SCmpLtU32:
    case GcnOpcode::SCmpGtU32:
        return true;
    default:
        return false;
    }
}

bool IsVectorAluOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::VMovB32:
    case GcnOpcode::VAddF32:
    case GcnOpcode::VSubF32:
    case GcnOpcode::VMulF32:
    case GcnOpcode::VMadF32:
    case GcnOpcode::VAddI32:
    case GcnOpcode::VSubI32:
    case GcnOpcode::VMulLoU32:
    case GcnOpcode::VMulHiU32:
    case GcnOpcode::VAndB32:
    case GcnOpcode::VOrB32:
    case GcnOpcode::VXorB32:
    case GcnOpcode::VCmpEqF32:
    case GcnOpcode::VCmpLtF32:
    case GcnOpcode::VCmpGtF32:
    case GcnOpcode::VCndmaskB32:
    case GcnOpcode::VCvtF32I32:
    case GcnOpcode::VCvtI32F32:
    case GcnOpcode::VCvtF32U32:
    case GcnOpcode::VCvtU32F32:
    case GcnOpcode::VCvtF32F16:
    case GcnOpcode::VCvtF16F32:
    case GcnOpcode::VRcpF32:
    case GcnOpcode::VRsqF32:
    case GcnOpcode::VSqrtF32:
    case GcnOpcode::VExpF32:
    case GcnOpcode::VLogF32:
    case GcnOpcode::VSinF32:
    case GcnOpcode::VCosF32:
    case GcnOpcode::VFloorF32:
    case GcnOpcode::VCeilF32:
    case GcnOpcode::VFractF32:
    case GcnOpcode::VMinF32:
    case GcnOpcode::VMaxF32:
    case GcnOpcode::VMinI32:
    case GcnOpcode::VMaxI32:
    case GcnOpcode::VReadfirstlaneB32:
    case GcnOpcode::VReadlaneB32:
    case GcnOpcode::VWritelaneB32:
        return true;
    default:
        return false;
    }
}

bool IsBranchOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::SCbranchScc0:
    case GcnOpcode::SCbranchScc1:
    case GcnOpcode::SCbranchVccz:
    case GcnOpcode::SCbranchVccnz:
    case GcnOpcode::SCbranchExecz:
    case GcnOpcode::SCbranchExecnz:
    case GcnOpcode::SBranch:
        return true;
    default:
        return false;
    }
}

bool IsScalarMemoryOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::SLoadDword:
    case GcnOpcode::SLoadDwordx2:
    case GcnOpcode::SLoadDwordx4:
    case GcnOpcode::SLoadDwordx8:
    case GcnOpcode::SLoadDwordx16:
        return true;
    default:
        return false;
    }
}

bool IsVectorMemoryOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::BufferLoadFormatX:
    case GcnOpcode::BufferLoadFormatXy:
    case GcnOpcode::BufferLoadFormatXyz:
    case GcnOpcode::BufferLoadFormatXyzw:
    case GcnOpcode::BufferLoadDword:
    case GcnOpcode::BufferLoadDwordx2:
    case GcnOpcode::BufferLoadDwordx4:
    case GcnOpcode::BufferStoreFormatX:
    case GcnOpcode::BufferStoreDword:
    case GcnOpcode::BufferStoreDwordx4:
    case GcnOpcode::FlatLoadDword:
    case GcnOpcode::FlatLoadDwordx2:
    case GcnOpcode::FlatLoadDwordx4:
    case GcnOpcode::FlatStoreDword:
    case GcnOpcode::FlatStoreDwordx2:
    case GcnOpcode::FlatStoreDwordx4:
        return true;
    default:
        return false;
    }
}

bool IsImageOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::ImageSample:
    case GcnOpcode::ImageSampleLz:
    case GcnOpcode::ImageLoad:
    case GcnOpcode::ImageStore:
        return true;
    default:
        return false;
    }
}

bool IsExportOpcode(GcnOpcode opcode) {
    switch (opcode) {
    case GcnOpcode::Exp:
        return true;
    default:
        return false;
    }
}

} // namespace ShaderRecompiler
