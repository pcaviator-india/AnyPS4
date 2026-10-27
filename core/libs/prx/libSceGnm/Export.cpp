#include <cstdint>
#include <cstddef>
#include <cstring>
#include <stdexcept>

#include "SceTypes.hpp"
#include "prx/libc/include/General.hpp"

extern "C" {

// PS4 NID-alias tables: stubs for PS4 GNM imports that resolve here instead of
// failing at load time. NIDs computed from PS4 symbol names (same SHA1+suffix
// scheme as PS5). Each maps to a NotImplemented stub so the import is present
// (Windows strict import resolution) but the function is unimplemented.

extern int APS5_VABI sceGnmSubmitAndFlipCommandBuffers_stub(void);

extern int APS5_VABI sceGnmInsertWaitFlipDone_stub(void);

extern int APS5_VABI sceGnmInsertWaitFlipDone_stub(void);

extern int APS5_VABI sceGnmAddEqEvent_stub(void);

APS5_EXPORT("b08AgtPlHPg", sceGnmAreSubmitsAllowed_stub);
int APS5_VABI sceGnmAreSubmitsAllowed_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("ihxrbsoSKWc", sceGnmBeginWorkload_stub);
int APS5_VABI sceGnmBeginWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("ffrNQOshows", sceGnmComputeWaitOnAddress_stub);
int APS5_VABI sceGnmComputeWaitOnAddress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("EJapNl2+pgU", sceGnmComputeWaitSemaphore_stub);
int APS5_VABI sceGnmComputeWaitSemaphore_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("5udAm+6boVg", sceGnmCreateWorkloadStream_stub);
int APS5_VABI sceGnmCreateWorkloadStream_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("qpGITzPE+Zc", sceGnmDebugHardwareStatus_stub);
int APS5_VABI sceGnmDebugHardwareStatus_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("PVT+fuoS9gU", sceGnmDeleteEqEvent_stub);
int APS5_VABI sceGnmDeleteEqEvent_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("UtObDRQiGbs", sceGnmDestroyWorkloadStream_stub);
int APS5_VABI sceGnmDestroyWorkloadStream_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("bX5IbRvECXk", sceGnmDingDong_stub);
int APS5_VABI sceGnmDingDong_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("byXlqupd8cE", sceGnmDingDongForWorkload_stub);
int APS5_VABI sceGnmDingDongForWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("HHo1BAljZO8", sceGnmDisableMipStatsReport_stub);
int APS5_VABI sceGnmDisableMipStatsReport_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("0BzLGljcwBo", sceGnmDispatchDirect_stub);
int APS5_VABI sceGnmDispatchDirect_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Z43vKp5k7r0", sceGnmDispatchIndirect_stub);
int APS5_VABI sceGnmDispatchIndirect_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("wED4ZXCFJT0", sceGnmDispatchIndirectOnMec_stub);
int APS5_VABI sceGnmDispatchIndirectOnMec_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("nF6bFRUBRAU", sceGnmDispatchInitDefaultHardwareState_stub);
int APS5_VABI sceGnmDispatchInitDefaultHardwareState_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmDrawIndex_stub(uint32_t indexCount, uint32_t startIndex, uint32_t primCount);

extern int APS5_VABI sceGnmDrawIndexAuto_stub(uint32_t indexCount);

extern int APS5_VABI sceGnmDrawIndexAuto_stub(uint32_t indexCount);

APS5_EXPORT("ED9-Fjr8Ta4", sceGnmDrawIndexIndirect_stub);
int APS5_VABI sceGnmDrawIndexIndirect_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("thbPcG7E7qk", sceGnmDrawIndexIndirectCountMulti_stub);
int APS5_VABI sceGnmDrawIndexIndirectCountMulti_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("jHdPvIzlpKc", sceGnmDrawIndexMultiInstanced_stub);
int APS5_VABI sceGnmDrawIndexMultiInstanced_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("oYM+YzfCm2Y", sceGnmDrawIndexOffset_stub);
int APS5_VABI sceGnmDrawIndexOffset_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("4v+otIIdjqg", sceGnmDrawIndirect_stub);
int APS5_VABI sceGnmDrawIndirect_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("cUCo8OvArrw", sceGnmDrawIndirectCountMulti_stub);
int APS5_VABI sceGnmDrawIndirectCountMulti_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmDrawInitDefaultHardwareState350_stub(void);

APS5_EXPORT("im2ZuItabu4", sceGnmDrawInitToDefaultContextState400_stub);
int APS5_VABI sceGnmDrawInitToDefaultContextState400_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("stDSYW2SBVM", sceGnmDrawOpaqueAuto_stub);
int APS5_VABI sceGnmDrawOpaqueAuto_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("TLV4mswiZ4A", sceGnmDriverCaptureInProgress_stub);
int APS5_VABI sceGnmDriverCaptureInProgress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("R6z1xM3pW-w", sceGnmDriverTraceInProgress_stub);
int APS5_VABI sceGnmDriverTraceInProgress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("d88anrgNoKY", sceGnmDriverTriggerCapture_stub);
int APS5_VABI sceGnmDriverTriggerCapture_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Fa3x75OOLRA", sceGnmEndWorkload_stub);
int APS5_VABI sceGnmEndWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("4Mv9OXypBG8", sceGnmFindResourcesPublic_stub);
int APS5_VABI sceGnmFindResourcesPublic_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("iBt3Oe00Kvc", sceGnmFlushGarlic_stub);
int APS5_VABI sceGnmFlushGarlic_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("UoYY0DWMC0U", sceGnmGetEqEventType_stub);
int APS5_VABI sceGnmGetEqEventType_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("H7-fgvEutM0", sceGnmGetEqTimeStamp_stub);
int APS5_VABI sceGnmGetEqTimeStamp_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("oL4hGI1PMpw", sceGnmGetGpuBlockStatus_stub);
int APS5_VABI sceGnmGetGpuBlockStatus_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Fwvh++m9IQI", sceGnmGetGpuCoreClockFrequency_stub);
int APS5_VABI sceGnmGetGpuCoreClockFrequency_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("tZCSL5ulnB4", sceGnmGetGpuInfoStatus_stub);
int APS5_VABI sceGnmGetGpuInfoStatus_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("iFirFzgYsvw", sceGnmGetLastWaitedAddress_stub);
int APS5_VABI sceGnmGetLastWaitedAddress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("KnldROUkWJY", sceGnmGetNumTcaUnits_stub);
int APS5_VABI sceGnmGetNumTcaUnits_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("FFVZcCu3zWU", sceGnmGetOffChipTessellationBufferSize_stub);
int APS5_VABI sceGnmGetOffChipTessellationBufferSize_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("QJjPjlmPAL0", sceGnmGetOwnerName_stub);
int APS5_VABI sceGnmGetOwnerName_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("dewXw5roLs0", sceGnmGetPhysicalCounterFromVirtualized_stub);
int APS5_VABI sceGnmGetPhysicalCounterFromVirtualized_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("fzJdEihTFV4", sceGnmGetProtectionFaultTimeStamp_stub);
int APS5_VABI sceGnmGetProtectionFaultTimeStamp_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("4PKnYXOhcx4", sceGnmGetResourceBaseAddressAndSizeInBytes_stub);
int APS5_VABI sceGnmGetResourceBaseAddressAndSizeInBytes_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("O0S96YnD04U", sceGnmGetResourceName_stub);
int APS5_VABI sceGnmGetResourceName_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("UBv7FkVfzcQ", sceGnmGetResourceShaderGuid_stub);
int APS5_VABI sceGnmGetResourceShaderGuid_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("bdqdvIkLPIU", sceGnmGetResourceType_stub);
int APS5_VABI sceGnmGetResourceType_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("UoBuWAhKk7U", sceGnmGetResourceUserData_stub);
int APS5_VABI sceGnmGetResourceUserData_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("nEyFbYUloIM", sceGnmGetShaderProgramBaseAddress_stub);
int APS5_VABI sceGnmGetShaderProgramBaseAddress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("k7iGTvDQPLQ", sceGnmGetShaderStatus_stub);
int APS5_VABI sceGnmGetShaderStatus_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("ln33zjBrfjk", sceGnmGetTheTessellationFactorRingBufferBaseAddress_stub);
int APS5_VABI sceGnmGetTheTessellationFactorRingBufferBaseAddress_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("NfvOrNzy6sk", sceGnmInsertDingDongMarker_stub);
int APS5_VABI sceGnmInsertDingDongMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("7qZVNgEu+SY", sceGnmInsertPopMarker_stub);
int APS5_VABI sceGnmInsertPopMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("aPIZJTXC+cU", sceGnmInsertPushColorMarker_stub);
int APS5_VABI sceGnmInsertPushColorMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("W1Etj-jlW7Y", sceGnmInsertPushMarker_stub);
int APS5_VABI sceGnmInsertPushMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("aj3L-iaFmyk", sceGnmInsertSetColorMarker_stub);
int APS5_VABI sceGnmInsertSetColorMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("jiItzS6+22g", sceGnmInsertSetMarker_stub);
int APS5_VABI sceGnmInsertSetMarker_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("jg33rEKLfVs", sceGnmIsUserPaEnabled_stub);
int APS5_VABI sceGnmIsUserPaEnabled_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("26PM5Mzl8zc", sceGnmLogicalCuIndexToPhysicalCuIndex_stub);
int APS5_VABI sceGnmLogicalCuIndexToPhysicalCuIndex_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("RU74kek-N0c", sceGnmLogicalCuMaskToPhysicalCuMask_stub);
int APS5_VABI sceGnmLogicalCuMaskToPhysicalCuMask_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Kl0Z3LH07QI", sceGnmLogicalTcaUnitToPhysical_stub);
int APS5_VABI sceGnmLogicalTcaUnitToPhysical_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("29oKvKXzEZo", sceGnmMapComputeQueue_stub);
int APS5_VABI sceGnmMapComputeQueue_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("A+uGq+3KFtQ", sceGnmMapComputeQueueWithPriority_stub);
int APS5_VABI sceGnmMapComputeQueueWithPriority_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("6IMbpR7nTzA", sceGnmQueryResourceRegistrationUserMemoryRequirements_stub);
int APS5_VABI sceGnmQueryResourceRegistrationUserMemoryRequirements_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("9Mv61HaMhfA", sceGnmRegisterGdsResource_stub);
int APS5_VABI sceGnmRegisterGdsResource_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("ZFqKFl23aMc", sceGnmRegisterOwner_stub);
int APS5_VABI sceGnmRegisterOwner_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmRegisterResource_stub(void* resourcePtr, uint32_t resourceType, uint64_t gpuAddress, uint64_t size);

APS5_EXPORT("gObODli-OH8", sceGnmRequestFlipAndSubmitDone_stub);
int APS5_VABI sceGnmRequestFlipAndSubmitDone_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("6YRHhh5mHCs", sceGnmRequestFlipAndSubmitDoneForWorkload_stub);
int APS5_VABI sceGnmRequestFlipAndSubmitDoneForWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("f85orjx7qts", sceGnmRequestMipStatsReportAndReset_stub);
int APS5_VABI sceGnmRequestMipStatsReportAndReset_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("MYRtYhojKdA", sceGnmResetVgtControl_stub);
int APS5_VABI sceGnmResetVgtControl_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Kx-h-nWQJ8A", sceGnmSetCsShaderWithModifier_stub);
int APS5_VABI sceGnmSetCsShaderWithModifier_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("X9Omw9dwv5M", sceGnmSetEmbeddedPsShader_stub);
int APS5_VABI sceGnmSetEmbeddedPsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("+AFvOEXrKJk", sceGnmSetEmbeddedVsShader_stub);
int APS5_VABI sceGnmSetEmbeddedVsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("FUHG8sQ3R58", sceGnmSetEsShader_stub);
int APS5_VABI sceGnmSetEsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("jtkqXpAOY6w", sceGnmSetGsRingSizes_stub);
int APS5_VABI sceGnmSetGsRingSizes_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmSetGsShader_stub(void* gsShaderPtr);

extern int APS5_VABI sceGnmSetHsShader_stub(void* hsShaderPtr);

extern int APS5_VABI sceGnmSetHsShader_stub(void* hsShaderPtr);

APS5_EXPORT("vckdzbQ46SI", sceGnmSetLsShader_stub);
int APS5_VABI sceGnmSetLsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmSetPsShader350_stub(void* psShaderPtr);

APS5_EXPORT("q-qhDxP67Hg", sceGnmSetResourceRegistrationUserMemory_stub);
int APS5_VABI sceGnmSetResourceRegistrationUserMemory_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("K3BKBBYKUSE", sceGnmSetResourceUserData_stub);
int APS5_VABI sceGnmSetResourceUserData_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("cFCp0NX8wf0", sceGnmSetVgtControl_stub);
int APS5_VABI sceGnmSetVgtControl_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmSetVsShader_stub(void* vsShaderPtr);

APS5_EXPORT("XiyzNZ9J4nQ", sceGnmSetWaveLimitMultipliers_stub);
int APS5_VABI sceGnmSetWaveLimitMultipliers_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("+xuDhxlWRPg", sceGnmSetupMipStatsReport_stub);
int APS5_VABI sceGnmSetupMipStatsReport_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Ga6r7H6Y0RI", sceGnmSubmitAndFlipCommandBuffersForWorkload_stub);
int APS5_VABI sceGnmSubmitAndFlipCommandBuffersForWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmSubmitCommandBuffers_stub(void* cmdBuffers, uint32_t numBuffers);

APS5_EXPORT("jRcI8VcgTz4", sceGnmSubmitCommandBuffersForWorkload_stub);
int APS5_VABI sceGnmSubmitCommandBuffersForWorkload_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmSubmitDone_stub(void);

APS5_EXPORT("ArSg-TGinhk", sceGnmUnmapComputeQueue_stub);
int APS5_VABI sceGnmUnmapComputeQueue_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("yhFCnaz5daw", sceGnmUnregisterAllResourcesForOwner_stub);
int APS5_VABI sceGnmUnregisterAllResourcesForOwner_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("fhKwCVVj9nk", sceGnmUnregisterOwnerAndResources_stub);
int APS5_VABI sceGnmUnregisterOwnerAndResources_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("k8EXkhIP+lM", sceGnmUnregisterResource_stub);
int APS5_VABI sceGnmUnregisterResource_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("nLM2i2+65hA", sceGnmUpdateGsShader_stub);
int APS5_VABI sceGnmUpdateGsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("GNlx+y7xPdE", sceGnmUpdateHsShader_stub);
int APS5_VABI sceGnmUpdateHsShader_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

extern int APS5_VABI sceGnmUpdatePsShader350_stub(void* psShaderPtr);

extern int APS5_VABI sceGnmUpdateVsShader_stub(void* vsShaderPtr);

APS5_EXPORT("SXw4dZEkgpA", sceGnmValidateDisableDiagnostics_stub);
int APS5_VABI sceGnmValidateDisableDiagnostics_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("BgM3t3LvcNk", sceGnmValidateDisableDiagnostics2_stub);
int APS5_VABI sceGnmValidateDisableDiagnostics2_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("qGP74T5OWJc", sceGnmValidateDispatchCommandBuffers_stub);
int APS5_VABI sceGnmValidateDispatchCommandBuffers_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("hsZPf1lON7E", sceGnmValidateDrawCommandBuffers_stub);
int APS5_VABI sceGnmValidateDrawCommandBuffers_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("RX7XCNSaL6I", sceGnmValidateGetDiagnosticInfo_stub);
int APS5_VABI sceGnmValidateGetDiagnosticInfo_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("5SHGNwLXBV4", sceGnmValidateGetDiagnostics_stub);
int APS5_VABI sceGnmValidateGetDiagnostics_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("HzMN7ANqYEc", sceGnmValidateGetVersion_stub);
int APS5_VABI sceGnmValidateGetVersion_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("rTIV11nMQuM", sceGnmValidateOnSubmitEnabled_stub);
int APS5_VABI sceGnmValidateOnSubmitEnabled_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("MBMa6EFu4Ko", sceGnmValidateResetState_stub);
int APS5_VABI sceGnmValidateResetState_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

APS5_EXPORT("Q7t4VEYLafI", sceGnmValidationRegisterMemoryCheckCallback_stub);
int APS5_VABI sceGnmValidationRegisterMemoryCheckCallback_stub(void) {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

} // extern "C"
