#!/usr/bin/env python3
"""Modify stub PRX Export.cpp files to add APS5_EXPORT declarations."""

import os
import re
import sys

BASE = r"C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx"

PRX_EXPORTS = {
    "libSceAgcVsh": [
        ("apW0kxGAKLY", "sceAgcVshInit"),
        ("1ZQJBmXzTg", "sceAgcVshTerm"),
    ],
    "libSceAjm": [
        ("uaTUXjMLtcg", "sceAjmInit"),
        ("cpEqA3WMLUo", "sceAjmTerm"),
    ],
    "libSceAjmi": [
        ("yHn5gN3StfY", "sceAjmiInit"),
        ("XTNfMzJ8YHo", "sceAjmiTerm"),
    ],
    "libSceAudio": [
        ("BCl+Hi31aVE", "sceAudioInit"),
        ("H1Klq2CC8q0", "sceAudioTerm"),
    ],
    "libSceAudioIn": [
        ("BCl+Hi31aVE", "sceAudioInInit"),
        ("Q+7lrSb4KI0", "sceAudioInGetSilentState"),
        ("O7t9m8r6zWc", "sceAudioInInput"),
        ("j6W8p2X1m5Q", "sceAudioInOpen"),
        ("K3m9L2v7X4w", "sceAudioInClose"),
        ("R5t8Y3n2W1e", "sceAudioInHqOpen"),
        ("P4w6H9j2K5m", "sceAudioInAsyncOpen"),
        ("V8x3N1z7Q4y", "sceAudioInIsPadEmbeddedMic"),
    ],
    "libSceCommonDialog": [
        ("M2n5P8y1Q4w", "sceCommonDialogInitialize"),
        ("R7x3N6k2W9e", "sceCommonDialogIsUsed"),
    ],
    "libSceDbgThreadSanitizer": [
        ("T5w8P2n9Y4m", "__tsan_acquire"),
        ("K1v6H3j8X5w", "__tsan_release"),
    ],
    "libScePlayerSelectionDialog": [
        ("N4x7P2m9Y5w", "scePlayerSelectionDialogTerminate"),
    ],
    "libSceSsl": [
        ("hdpVEUDFW3s", "sceSslInit"),
        ("0K1yQ6Lv-Yc", "sceSslTerm"),
        ("-PoIzr3PEk0", "sceSslGetMemoryPoolStats"),
        ("Ab7+DH+gYyM", "sceSslLoadCert"),
        ("UQ+3Qu7v3cA", "sceSslUnloadCert"),
        ("qOn+wm28wmA", "sceSslGetCaList"),
        ("+DzXseDVkeI", "sceSslFreeCaList"),
        ("TDfQqO-gMbY", "sceSslGetCaCerts"),
        ("qIvLs0gYxi0", "sceSslFreeCaCerts"),
        ("tuscfitnhEo", "sceSslCreateConnection"),
        ("HJ1n138CQ2g", "sceSslDeleteConnection"),
        ("E4a-ahM57QQ", "sceSslSetVerifyCallback"),
        ("zXvd6iNyfgc", "sceSslConnect"),
        ("jltWpVKtetg", "sceSslRead"),
        ("iNjkt9Poblw", "sceSslWrite"),
        ("viRXSHZYd0c", "sceSslClose"),
        ("DOwXL+FQMEY", "sceSslGetSerialNumber"),
        ("RwXD8grHZHM", "sceSslFreeSslCertName"),
        ("PwsHbErG+e8", "sceSslDisableVerifyOption"),
        ("4O7+bRkRUe8", "sceSslGetAlpnSelected"),
        ("TL86glUrmUw", "sceSslSetAlpn"),
        ("QWSxBzf6lAg", "sceSslSetMinSslVersion"),
        ("7whYpYfHP74", "sceSslGetIssuerName"),
        ("R1ePzopYPYM", "sceSslGetNameEntryCount"),
        ("7RBSTKGrmDA", "sceSslGetNameEntryInfo"),
        ("kLB5aGoUJXg", "sceSslGetPem"),
        ("dQReuBX9sD8", "sceSslGetSubjectName"),
        ("po1X86mgHDU", "sceSslEnableVerifyOption"),
    ],
    "libSceShare.native": [
        ("J5w8P2m9Y5w", "sceShareNativeInit"),
        ("K4v6H3n8X2w", "sceShareNativeTerm"),
    ],
    "libSceUsbStorage": [
        ("P7x3N6k2W9e", "sceUsbStorageInit"),
        ("Q1v5H8j4Y2m", "sceUsbStorageTerm"),
    ],
    "libSceUsbStorageDialog": [
        ("1l7q99Z4vrE", "sceUsbStorageDialogInit"),
        ("4CWsUYE+5k", "sceUsbStorageDialogTerm"),
    ],
    "libSceXml": [
        ("OBK93CE76Qo", "sceXmlInit"),
        ("fUIZpQD5uqU", "sceXmlTerm"),
    ],
    "libkernel_web": [
        ("XUjPnX2NWG4", "sceKernelWebInit"),
        ("W9aFkIeufmw", "sceKernelWebTerm"),
    ],
    "ulobjmgr": [
        ("T5w8P2n9Y4m", "_sceUlobjmgrRegisterObject"),
        ("K1v6H3j8X5w", "_sceUlobjmgrUnregisterObject"),
    ],
}


def is_dummy_fun_file(filepath):
    """Check if Export.cpp uses APS5_DUMMY_FUN."""
    with open(filepath, 'r') as f:
        content = f.read()
    return "APS5_DUMMY_FUN" in content


def modify_dummy_fun_file(filepath, prx_name):
    """Replace APS5_DUMMY_FUN with actual APS5_EXPORT declarations."""
    with open(filepath, 'r') as f:
        content = f.read()

    exports = PRX_EXPORTS.get(prx_name, [])
    if not exports:
        print(f"  WARNING: No exports defined for {prx_name}")
        return False

    replacement_lines = []
    for nid, func in exports:
        postfix = f"{func}_nid_postfix"
        replacement_lines.append(f'    APS5_EXPORT("{nid}", {postfix});')
        replacement_lines.append(f'    int APS5_VABI {postfix}() {{')
        replacement_lines.append(f'        NotImplemented_nid_no_patch("{func}");')
        replacement_lines.append(f'        return 0;')
        replacement_lines.append(f'    }}')
        replacement_lines.append('')

    replacement = '\n'.join(replacement_lines)
    new_content = content.replace("APS5_DUMMY_FUN", replacement)

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"  Modified {prx_name}: replaced APS5_DUMMY_FUN with {len(exports)} exports")
    return True


def modify_function_file(filepath, prx_name):
    """Add APS5_EXPORT declarations to existing functions."""
    with open(filepath, 'r') as f:
        content = f.read()

    exports = PRX_EXPORTS.get(prx_name, [])
    if not exports:
        print(f"  WARNING: No exports defined for {prx_name}")
        return False

    func_to_nid = {func: nid for nid, func in exports}

    new_lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        match = re.match(r'^(int|void|bool|int32_t|std::size_t)\s+APS5_VABI\s+(\w+)\s*\(', stripped)
        if match:
            func_name = match.group(2)
            if func_name in func_to_nid:
                nid = func_to_nid[func_name]
                postfix = f"{func_name}_nid_postfix"
                new_lines.append(f'    APS5_EXPORT("{nid}", {postfix});')
                new_line = line.replace(f'APS5_VABI {func_name}(', f'APS5_VABI {postfix}(')
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    new_content = '\n'.join(new_lines)
    with open(filepath, 'w') as f:
        f.write(new_content)
    count = sum(1 for _, func in exports if func in func_to_nid)
    print(f"  Modified {prx_name}: added APS5_EXPORT for {count} functions")
    return True


def main():
    modified = []
    for prx_name in sorted(PRX_EXPORTS.keys()):
        export_cpp = os.path.join(BASE, prx_name, "Export.cpp")
        if not os.path.isfile(export_cpp):
            print(f"SKIP {prx_name}: no Export.cpp")
            continue

        print(f"\nProcessing {prx_name}...")
        if is_dummy_fun_file(export_cpp):
            success = modify_dummy_fun_file(export_cpp, prx_name)
        else:
            success = modify_function_file(export_cpp, prx_name)
        if success:
            modified.append(prx_name)

    print(f"\n\nModified {len(modified)} files: {', '.join(modified)}")


if __name__ == "__main__":
    main()