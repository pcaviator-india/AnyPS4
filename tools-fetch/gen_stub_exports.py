#!/usr/bin/env python3
"""Generate APS5_EXPORT lines for stub PRXs to convert them to full Windows DLLs.

Reads the NID database, computes NIDs for known PS4 symbol names, and outputs
APS5_EXPORT lines that can be added to each stub PRX's Export.cpp.

Usage:
    python gen_stub_exports.py <nid_db_path> [--prx <prx_name>]
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nid_db import NidDatabase, compute_nid

# Map of stub PRX -> list of PS4 symbol names that need to be exported
# These are the functions found in each stub PRX's source that lack APS5_EXPORT
STUB_FUNCTIONS = {
    "libSceSsl": [
        "sceSslInit", "sceSslTerm", "sceSslGetMemoryPoolStats",
        "sceSslLoadCert", "sceSslUnloadCert", "sceSslGetCaList",
        "sceSslFreeCaList", "sceSslGetCaCerts", "sceSslFreeCaCerts",
        "sceSslCreateConnection", "sceSslDeleteConnection",
        "sceSslSetVerifyCallback", "sceSslConnect", "sceSslRead",
        "sceSslWrite", "sceSslClose", "sceSslGetSerialNumber",
        "sceSslFreeSslCertName", "sceSslDisableVerifyOption",
        "sceSslGetAlpnSelected", "sceSslSetAlpn",
        "sceSslSetMinSslVersion", "sceSslGetIssuerName",
        "sceSslGetNameEntryCount", "sceSslGetNameEntryInfo",
        "sceSslGetPem", "sceSslGetSubjectName",
        "sceSslEnableVerifyOption",
    ],
    "libSceAudioIn": [
        "sceAudioInInit", "sceAudioInGetSilentState",
        "sceAudioInInput", "sceAudioInOpen",
        "sceAudioInClose", "sceAudioInHqOpen",
        "sceAudioInAsyncOpen", "sceAudioInIsPadEmbeddedMic",
    ],
    "libSceAjm": ["sceAjmInit", "sceAjmTerm"],
    "libSceAjmi": ["sceAjmiInit", "sceAjmiTerm"],
    "libSceAudio": ["sceAudioInit", "sceAudioTerm"],
    "libSceShare.native": ["sceShareNativeInit", "sceShareNativeTerm"],
    "libSceUsbStorage": ["sceUsbStorageInit", "sceUsbStorageTerm"],
    "libSceUsbStorageDialog": ["sceUsbStorageDialogInit", "sceUsbStorageDialogTerm"],
    "libSceXml": ["sceXmlInit", "sceXmlTerm"],
    "libkernel_web": ["sceKernelWebInit", "sceKernelWebTerm"],
    "libSceAgcVsh": ["sceAgcVshInit", "sceAgcVshTerm"],
    "libScePlayerSelectionDialog": ["scePlayerSelectionDialogInit", "scePlayerSelectionDialogTerminate"],
    "libSceRandom": ["sceRandomGetRandomNumber"],
}


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    nid_db_path = argv[0]
    target_prx = None
    i = 1
    while i < len(argv):
        if argv[i] == "--prx" and i + 1 < len(argv):
            target_prx = argv[i + 1]
            i += 2
        else:
            i += 1

    if not os.path.isfile(nid_db_path):
        print(f"ERROR: NID database not found: {nid_db_path}")
        print("  Provide aerolib.csv or a JSON NID database")
        return 2

    nid_db = NidDatabase()
    count = nid_db.load(nid_db_path)
    print(f"Loaded {count} NID entries from {nid_db_path}")
    print()

    prxs_to_process = [target_prx] if target_prx else sorted(STUB_FUNCTIONS.keys())

    for prx in prxs_to_process:
        if prx not in STUB_FUNCTIONS:
            print(f"WARNING: {prx} not in stub functions map, skipping")
            continue

        print(f"=== {prx} ===")
        print(f"// Add these to AnyPS4/core/libs/prx/{prx}/Export.cpp")
        print()

        for symbol in STUB_FUNCTIONS[prx]:
            nid = compute_nid(symbol)
            # Check if NID is already known
            known_name = nid_db.lookup(nid)
            status = f" // {known_name}" if known_name else ""
            print(f'APS5_EXPORT("{nid}", {symbol}_nid_postfix);')
            print(f'int APS5_VABI {symbol}_nid_postfix() {{')
            print(f'    NotImplemented_nid_no_patch("{symbol}");')
            print(f'    return 0;')
            print(f'}}')
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))