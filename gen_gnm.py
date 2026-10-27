#!/usr/bin/env python3
"""
gen_gnm.py - Generate NID-to-function mappings for libSceGnm exports.
"""
import hashlib
import base64
import sys
import os
import re

SUFFIX = bytes([0x51, 0x8D, 0x64, 0xA6, 0x35, 0xDE, 0xD8, 0xC1,
                0xE6, 0xB0, 0x39, 0xB1, 0xC3, 0xE5, 0x52, 0x30])
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-'
STD_B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
_B64_INDEX = {c: i for i, c in enumerate(STD_B64)}


def compute_nid(function_name):
    digest = hashlib.sha1(function_name.encode() + SUFFIX).digest()
    reversed_bytes = digest[7::-1]
    full_b64 = base64.b64encode(reversed_bytes).decode()
    return ''.join(ALPHABET[_B64_INDEX[c]] for c in full_b64[:11])


def read_imports(imports_path):
    imports = set()
    if not os.path.exists(imports_path):
        return imports
    with open(imports_path) as f:
        for line in f:
            line = line.strip()
            if line:
                imports.add(line)
    return imports


def read_imports_raw(raw_path):
    nids = set()
    if not os.path.exists(raw_path):
        return nids
    with open(raw_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.search(r'#([#A-Za-z0-9+-]+)$', line)
            if m:
                nids.add(m.group(1))
    return nids


GNM_FUNCTIONS = [
    'sceGnmSubmitAndFlipCommandBuffers',
    'sceGnmSubmitAndFlipCommandBuffersForWorkload',
    'sceGnmSubmitCommandBuffers',
    'sceGnmSubmitCommandBuffersForWorkload',
    'sceGnmSubmitDone',
    'sceGnmInsertWaitFlipDone',
    'sceGnmWaitFlip',
    'sceGnmSetVsShader', 'sceGnmSetHsShader', 'sceGnmSetDsShader',
    'sceGnmSetGsShader', 'sceGnmSetPsShader350', 'sceGnmSetCsShaderWithModifier',
    'sceGnmSetEmbeddedVsShader', 'sceGnmSetEmbeddedPsShader',
    'sceGnmSetEsShader', 'sceGnmSetLsShader',
    'sceGnmUpdateVsShader', 'sceGnmUpdateHsShader', 'sceGnmUpdateDsShader',
    'sceGnmUpdateGsShader', 'sceGnmUpdatePsShader350', 'sceGnmUpdateCsShader',
    'sceGnmValidateGetVersion', 'sceGnmValidateGetDiagnostics',
    'sceGnmValidateGetDiagnosticInfo', 'sceGnmValidateOnSubmitEnabled',
    'sceGnmValidateResetState', 'sceGnmValidateDisableDiagnostics',
    'sceGnmValidateDisableDiagnostics2', 'sceGnmValidateDrawCommandBuffers',
    'sceGnmValidateDispatchCommandBuffers',
    'sceGnmValidationRegisterMemoryCheckCallback',
    'sceGnmRegisterOwner', 'sceGnmRegisterResource', 'sceGnmUnregisterResource',
    'sceGnmUnregisterOwnerAndResources', 'sceGnmUnregisterAllResourcesForOwner',
    'sceGnmRegisterGdsResource', 'sceGnmSetResourceUserData',
    'sceGnmSetResourceRegistrationUserMemory',
    'sceGnmQueryResourceRegistrationUserMemoryRequirements',
    'sceGnmGetResourceType', 'sceGnmGetResourceBaseAddressAndSizeInBytes',
    'sceGnmGetResourceName', 'sceGnmGetResourceShaderGuid',
    'sceGnmGetResourceUserData', 'sceGnmGetShaderProgramBaseAddress',
    'sceGnmGetShaderStatus', 'sceGnmFindResourcesPublic',
    'sceGnmDrawIndex', 'sceGnmDrawIndexAuto', 'sceGnmDrawIndexIndirect',
    'sceGnmDrawIndexIndirectCountMulti', 'sceGnmDrawIndexMultiInstanced',
    'sceGnmDrawIndexOffset', 'sceGnmDrawIndirect', 'sceGnmDrawIndirectCountMulti',
    'sceGnmDrawOpaqueAuto', 'sceGnmDrawInitDefaultHardwareState350',
    'sceGnmDrawInitToDefaultContextState400', 'sceGnmDispatchDirect',
    'sceGnmDispatchIndirect', 'sceGnmDispatchIndirectOnMec',
    'sceGnmDispatchInitDefaultHardwareState',
    'sceGnmInsertPushMarker', 'sceGnmInsertPopMarker', 'sceGnmInsertSetMarker',
    'sceGnmInsertPushColorMarker', 'sceGnmInsertSetColorMarker',
    'sceGnmInsertDingDongMarker', 'sceGnmDebugHardwareStatus',
    'sceGnmRequestMipStatsReportAndReset', 'sceGnmSetupMipStatsReport',
    'sceGnmDisableMipStatsReport',
    'sceGnmBeginWorkload', 'sceGnmEndWorkload',
    'sceGnmCreateWorkloadStream', 'sceGnmDestroyWorkloadStream',
    'sceGnmMapComputeQueue', 'sceGnmMapComputeQueueWithPriority',
    'sceGnmUnmapComputeQueue', 'sceGnmDingDong', 'sceGnmDingDongForWorkload',
    'sceGnmAddEqEvent', 'sceGnmDeleteEqEvent',
    'sceGnmGetEqEventType', 'sceGnmGetEqTimeStamp',
    'sceGnmComputeWaitOnAddress', 'sceGnmComputeWaitSemaphore',
    'sceGnmAreSubmitsAllowed', 'sceGnmFlushGarlic',
    'sceGnmGetGpuBlockStatus', 'sceGnmGetGpuCoreClockFrequency',
    'sceGnmGetGpuInfoStatus', 'sceGnmGetLastWaitedAddress',
    'sceGnmGetNumTcaUnits', 'sceGnmGetOffChipTessellationBufferSize',
    'sceGnmGetOwnerName', 'sceGnmGetPhysicalCounterFromVirtualized',
    'sceGnmGetProtectionFaultTimeStamp',
    'sceGnmGetTheTessellationFactorRingBufferBaseAddress',
    'sceGnmIsUserPaEnabled', 'sceGnmLogicalCuIndexToPhysicalCuIndex',
    'sceGnmLogicalCuMaskToPhysicalCuMask', 'sceGnmLogicalTcaUnitToPhysical',
    'sceGnmResetVgtControl', 'sceGnmSetGsRingSizes', 'sceGnmSetVgtControl',
    'sceGnmSetWaveLimitMultipliers',
    'sceGnmDriverCaptureInProgress', 'sceGnmDriverTraceInProgress',
    'sceGnmDriverTriggerCapture',
    'sceGnmRequestFlipAndSubmitDone', 'sceGnmRequestFlipAndSubmitDoneForWorkload',
]


def generate_preserve_exports(imports_path, output_path):
    imports = read_imports(imports_path)
    count = 0
    with open(output_path, 'w') as f:
        for func_name in GNM_FUNCTIONS:
            n = compute_nid(func_name)
            if n in imports:
                f.write(n + '\n')
                count += 1
    return count


def generate_export_cpp(output_path, imports_path=None):
    imports = read_imports(imports_path) if imports_path else None
    count = 0
    with open(output_path, 'w') as f:
        f.write('// Auto-generated by gen_gnm.py - DO NOT EDIT\n')
        f.write('#include <cstdint>\n')
        f.write('#include "prx/libc/include/General.hpp"\n')
        f.write('#include "prx/libSceGnm/include/Gnm.hpp"\n')
        f.write('extern "C" {\n\n')
        for func_name in GNM_FUNCTIONS:
            n = compute_nid(func_name)
            stub_name = func_name + '_stub'
            if imports is None or n in imports:
                f.write(f'APS5_EXPORT("{n}", {stub_name});\n')
                f.write(f'int APS5_VABI {stub_name}(void) {{ NotImplemented_nid_no_patch("{func_name}"); return 0; }}\n\n')
                count += 1
        f.write('} // extern "C"\n')
    return count


def verify_mapping(imports_raw_path):
    gnm_nids = read_imports_raw(imports_raw_path)
    found = 0
    not_found = []
    for func_name in GNM_FUNCTIONS:
        n = compute_nid(func_name)
        if n in gnm_nids:
            found += 1
        else:
            not_found.append((func_name, n))
    print(f'Matched: {found}/{len(GNM_FUNCTIONS)}')
    if not_found:
        print('Not found in imports:')
        for func_name, n in not_found:
            print(f'  {func_name} -> {n}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gen_gnm.py <command> [args...]")
        print("  preserve-exports <imports.txt> <output.txt>")
        print("  export-cpp <output.cpp> [imports.txt]")
        print("  verify <imports_raw.txt>")
        sys.exit(1)
    command = sys.argv[1]
    if command == 'preserve-exports':
        count = generate_preserve_exports(sys.argv[2], sys.argv[3])
        print(f'Wrote {count} entries to {sys.argv[3]}')
    elif command == 'export-cpp':
        imports_path = sys.argv[3] if len(sys.argv) > 3 else None
        count = generate_export_cpp(sys.argv[2], imports_path)
        print(f'Wrote {count} export entries to {sys.argv[2]}')
    elif command == 'verify':
        verify_mapping(sys.argv[2])
    else:
        print(f'Unknown command: {command}')
        sys.exit(1)