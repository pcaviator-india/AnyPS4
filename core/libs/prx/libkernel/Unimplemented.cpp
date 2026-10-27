#include <cstdint>
#include <cstddef>
#include "SceTypes.hpp"
#include "prx/libc/include/General.hpp"

extern "C" {

int APS5_VABI __tls_get_addr_nid_postfix(void) {
    NotImplemented_nid_no_patch("vNe1w4diLCs");
    return 0;
}

APS5_EXPORT("AC1FtjqMCL0", sceKernelUnknown03);
int APS5_VABI sceKernelUnknown03(void) {
    NotImplemented_nid_no_patch("AC1FtjqMCL0");
    return 0;
}

APS5_EXPORT("0iEKNAvT600", sceKernelUnknown04);
int APS5_VABI sceKernelUnknown04(void) {
    NotImplemented_nid_no_patch("0iEKNAvT600");
    return 0;
}

APS5_EXPORT("2cELEBPdYQ0", sceKernelUnknown05);
int APS5_VABI sceKernelUnknown05(void) {
    NotImplemented_nid_no_patch("2cELEBPdYQ0");
    return 0;
}

APS5_EXPORT("5xYxiOtOccA", sceKernelUnknown06);
int APS5_VABI sceKernelUnknown06(void) {
    NotImplemented_nid_no_patch("5xYxiOtOccA");
    return 0;
}

APS5_EXPORT("6W+shIH315Q", sceKernelUnknown07);
int APS5_VABI sceKernelUnknown07(void) {
    NotImplemented_nid_no_patch("6W+shIH315Q");
    return 0;
}

APS5_EXPORT("7ilObq815O4", sceKernelUnknown08);
int APS5_VABI sceKernelUnknown08(void) {
    NotImplemented_nid_no_patch("7ilObq815O4");
    return 0;
}

APS5_EXPORT("7iq7Hfs8HBk", sceKernelUnknown09);
int APS5_VABI sceKernelUnknown09(void) {
    NotImplemented_nid_no_patch("7iq7Hfs8HBk");
    return 0;
}

APS5_EXPORT("AMJZhpC+siY", sceKernelUnknown10);
int APS5_VABI sceKernelUnknown10(void) {
    NotImplemented_nid_no_patch("AMJZhpC+siY");
    return 0;
}

APS5_EXPORT("E9XkHowt+dY", sceKernelUnknown11);
int APS5_VABI sceKernelUnknown11(void) {
    NotImplemented_nid_no_patch("E9XkHowt+dY");
    return 0;
}

APS5_EXPORT("GADjreszOgM", sceKernelUnknown12);
int APS5_VABI sceKernelUnknown12(void) {
    NotImplemented_nid_no_patch("GADjreszOgM");
    return 0;
}

APS5_EXPORT("Giyg2xGrXDU", sceKernelUnknown13);
int APS5_VABI sceKernelUnknown13(void) {
    NotImplemented_nid_no_patch("Giyg2xGrXDU");
    return 0;
}

APS5_EXPORT("KC3y21wrqzc", sceKernelUnknown14);
int APS5_VABI sceKernelUnknown14(void) {
    NotImplemented_nid_no_patch("KC3y21wrqzc");
    return 0;
}

APS5_EXPORT("Qb8wS4GZUsw", sceKernelUnknown15);
int APS5_VABI sceKernelUnknown15(void) {
    NotImplemented_nid_no_patch("Qb8wS4GZUsw");
    return 0;
}

APS5_EXPORT("aAQZSjb2fho", sceKernelUnknown16);
int APS5_VABI sceKernelUnknown16(void) {
    NotImplemented_nid_no_patch("aAQZSjb2fho");
    return 0;
}

APS5_EXPORT("pnz21I6VjDs", sceKernelUnknown17);
int APS5_VABI sceKernelUnknown17(void) {
    NotImplemented_nid_no_patch("pnz21I6VjDs");
    return 0;
}

APS5_EXPORT("qk043QPsrZU", sceKernelUnknown18);
int APS5_VABI sceKernelUnknown18(void) {
    NotImplemented_nid_no_patch("qk043QPsrZU");
    return 0;
}

APS5_EXPORT("uDGXwUKqi8s", sceKernelUnknown19);
int APS5_VABI sceKernelUnknown19(void) {
    NotImplemented_nid_no_patch("uDGXwUKqi8s");
    return 0;
}

// PS4 NID-alias tables: map PS4-imported NIDs to existing libkernel
// implementations. NIDs computed from PS4 symbol names (same SHA1+suffix
// scheme as PS5); PS4 games importing by these NIDs resolve here.
APS5_EXPORT("wzvqT4UqKX8", sceKernelLoadStartModule);
APS5_EXPORT("bMMArNdQ-N8", sceKernelStopUnloadModule);
APS5_EXPORT("oNvROPSEQAM", sceKernelLoadStartModule);
APS5_EXPORT("kOCZr2bEYFY", sceKernelStopUnloadModule);

// sceKernelExitThread is imported by PS4 titles but not yet implemented;
// provide a stub so the import resolves rather than failing at load time.
APS5_EXPORT("Nk4Ar0dg-iw", sceKernelExitThread_stub);
int APS5_VABI sceKernelExitThread_stub(void) {
    NotImplemented_nid_no_patch("Nk4Ar0dg-iw");
    return 0;
}

// sceKernelIsNeoMode reports whether the system is running in PS4 Pro / Neo mode.
// Returning 0 indicates base PS4 mode.
APS5_EXPORT("WslcK1FQcGI", sceKernelIsNeoMode_stub);
int APS5_VABI sceKernelIsNeoMode_stub(void) {
    return 0;
}
}
