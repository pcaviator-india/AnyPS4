#include <cstdint>
#include <cstddef>
#include <cstdlib>
#include <cstdio>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif
#include "SceTypes.hpp"
#include "prx/libc/include/General.hpp"
#include "prx/libc/include/HeapDiagnostics.hpp"

uint32_t Need_sceLibc = 1;

extern "C" {

    int APS5_VABI _ZSt13_Execute_onceRSt9once_flagPFiPvS1_PS1_ES1__nid_postfix(int*, int (APS5_VABI *)(void*, void*, void**), void*);

    int APS5_VABI std_execute_once_nid_postfix(int* flag, int (APS5_VABI *func)(void*, void*, void**), void* arg) {
        return _ZSt13_Execute_onceRSt9once_flagPFiPvS1_PS1_ES1__nid_postfix(flag, func, arg);
    }

    void APS5_VABI LibcHeapGetTraceInfo_nid_postfix(LibcHeapInfo* info) {
        LibcHeapTraceInfo_nid_no_patch(info);
    }

// Dead import of Cyberpunk 2077 (PPSA04029): no call sites, but the
// Windows loader resolves imports strictly, so it must be present.
int APS5_VABI _ZSt14_Atomic_assertPKcS0__nid_postfix() {
 NotImplemented_nid_no_patch(__func__);
 return 0;
}


APS5_EXPORT("H2e8t5ScQGc", libc___cxa_finalize);
void APS5_VABI libc___cxa_finalize(void* dsoHandle) {
    CxaFinalize_nid_no_patch(dsoHandle);
}

// PS4 NID-alias tables: map PS4-imported NIDs to existing libc
// implementations. NIDs computed from PS4 symbol names (same SHA1+suffix
// scheme as PS5); PS4 games importing by these NIDs resolve here.
APS5_EXPORT("Q3VBxCXhUHs", memcpy_nid_postfix);
APS5_EXPORT("8zTFvBIAIN8", memset_nid_postfix);
APS5_EXPORT("j4ViWNHEgww", strlen_nid_postfix);
APS5_EXPORT("Ovb2dSJOAuE", strcmp_nid_postfix);
APS5_EXPORT("aesyjrHVWy4", strncmp_nid_postfix);
APS5_EXPORT("kiZSXIWd9vg", strcpy_nid_postfix);
APS5_EXPORT("6sJWiWSRuqk", strncpy_nid_postfix);
APS5_EXPORT("gQX+4GDQjpM", malloc_nid_postfix);
APS5_EXPORT("tIhsqj0qsFE", free_nid_postfix);
APS5_EXPORT("2X5agFjKxMc", calloc_nid_postfix);
APS5_EXPORT("Y7aJ1uydPMo", realloc_nid_postfix);
APS5_EXPORT("hcuQgD53UxM", printf_nid_postfix);
APS5_EXPORT("tcVi5SivF7Q", sprintf_nid_postfix);
APS5_EXPORT("eLdDw6l0-bU", snprintf_nid_postfix);
APS5_EXPORT("jbz9I9vkqkk", vsprintf_nid_postfix);
APS5_EXPORT("Q2V+iqvjgC0", vsnprintf_nid_postfix);

// PS4 imports with no libc implementation yet: provide stubs so the
// import resolves rather than failing at load time.
APS5_EXPORT("wuCroIGjt2g", open_stub);
int APS5_VABI open_stub(const char* path, int flags, ...) {
    (void)path;
    (void)flags;
    NotImplemented_nid_no_patch("open_stub");
    return -1;
}

APS5_EXPORT("bY-PO6JhzhQ", close_stub);
int APS5_VABI close_stub(int fd) {
    (void)fd;
    NotImplemented_nid_no_patch("close_stub");
    return -1;
}

APS5_EXPORT("AqBioC2vF3I", read_stub);
int APS5_VABI read_stub(int fd, void* buf, size_t count) {
    (void)fd;
    (void)buf;
    (void)count;
    NotImplemented_nid_no_patch("read_stub");
    return -1;
}

APS5_EXPORT("FN4gaPmuFV8", write_stub);
int APS5_VABI write_stub(int fd, const void* buf, size_t count) {
    (void)fd;
    (void)buf;
    (void)count;
    NotImplemented_nid_no_patch("write_stub");
    return -1;
}

APS5_EXPORT("uMei1W9uyNo", exit_stub);
[[noreturn]] void APS5_VABI exit_stub(int status) {
    (void)status;
    NotImplemented_nid_no_patch("exit_stub");
    std::abort();
}

APS5_EXPORT("L1SBTkC+Cvw", abort_stub);
[[noreturn]] void APS5_VABI abort_stub(void) {
    NotImplemented_nid_no_patch("abort_stub");
    std::abort();
}

// PS4 semantic shims: mmap/threads stubs so PS4 game imports resolve.
// Return safe defaults (MAP_FAILED / -1) so callers can detect failure.
APS5_EXPORT("BPE9s9vQQXo", mmap_stub);
void* APS5_VABI mmap_stub(void* addr, std::size_t len, int prot, int flags, int fd, std::int64_t offset) {
    (void)addr;
    (void)len;
    (void)prot;
    (void)flags;
    (void)fd;
    (void)offset;
    NotImplemented_nid_no_patch("mmap_stub");
    return reinterpret_cast<void*>(-1);  // MAP_FAILED
}

APS5_EXPORT("UqDGjXA5yUM", munmap_stub);
int APS5_VABI munmap_stub(void* addr, std::size_t len) {
    (void)addr;
    (void)len;
    NotImplemented_nid_no_patch("munmap_stub");
    return -1;
}

APS5_EXPORT("YQOfxL4QfeU", mprotect_stub);
int APS5_VABI mprotect_stub(void* addr, std::size_t len, int prot) {
    (void)addr;
    (void)len;
    (void)prot;
    NotImplemented_nid_no_patch("mprotect_stub");
    return -1;
}

APS5_EXPORT("OxhIB8LB-PQ", pthread_create_stub);
int APS5_VABI pthread_create_stub(unsigned long* thread, const void* attr, void* (*start_routine)(void*), void* arg) {
    (void)thread;
    (void)attr;
    (void)start_routine;
    (void)arg;
    NotImplemented_nid_no_patch("pthread_create_stub");
    return -1;  // ENOSYS/EAGAIN equivalent
}

// PS4 import with no known implementation: provide stub so the import
// resolves rather than failing at load time. NID WslcK1FQcGI is unresolved
// by existing stubs; this stub allows the game to proceed past it.
// The APS5_EXPORT macro creates WslcK1FQcGI_nid_no_patch_cut; the NID
// patcher strips _nid_no_patch_cut to produce WslcK1FQcGI.
APS5_EXPORT("WslcK1FQcGI", unknown_WslcK1FQcGI_stub);
int APS5_VABI unknown_WslcK1FQcGI_stub() {
    NotImplemented_nid_no_patch("unknown_WslcK1FQcGI_stub");
    return 0;
}
    APS5_EXPORT("St4apgcBNfo", unknown_St4apgcBNfo_stub);
    int APS5_VABI unknown_St4apgcBNfo_stub(void) {
        NotImplemented_nid_no_patch("unknown_St4apgcBNfo_stub");
        return 0;
    }

    APS5_EXPORT("0z45PIH+SNI", unknown_0z45PIH_SNI_stub);
    int APS5_VABI unknown_0z45PIH_SNI_stub(void) {
        NotImplemented_nid_no_patch("unknown_0z45PIH_SNI_stub");
        return 0;
    }

    APS5_EXPORT("BMR4F-Uek3E", unknown_BMR4F_Uek3E_stub);
    int APS5_VABI unknown_BMR4F_Uek3E_stub(void) {
        NotImplemented_nid_no_patch("unknown_BMR4F_Uek3E_stub");
        return 0;
    }

    APS5_EXPORT("VwadwBBBJ80", unknown_VwadwBBBJ80_stub);
    int APS5_VABI unknown_VwadwBBBJ80_stub(void) {
        NotImplemented_nid_no_patch("unknown_VwadwBBBJ80_stub");
        return 0;
    }

    APS5_EXPORT("S1GkePI17zQ", unknown_S1GkePI17zQ_stub);
    int APS5_VABI unknown_S1GkePI17zQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_S1GkePI17zQ_stub");
        return 0;
    }

    APS5_EXPORT("xENtRue8dpI", unknown_xENtRue8dpI_stub);
    int APS5_VABI unknown_xENtRue8dpI_stub(void) {
        NotImplemented_nid_no_patch("unknown_xENtRue8dpI_stub");
        return 0;
    }


    APS5_EXPORT("mpxAdqW7dKY", unknown_mpxAdqW7dKY_stub);
    int APS5_VABI unknown_mpxAdqW7dKY_stub(void) {
        NotImplemented_nid_no_patch("unknown_mpxAdqW7dKY_stub");
        return 0;
    }

    APS5_EXPORT("2xxUtuC-RzE", unknown_2xxUtuC_RzE_stub);
    int APS5_VABI unknown_2xxUtuC_RzE_stub(void) {
        NotImplemented_nid_no_patch("unknown_2xxUtuC_RzE_stub");
        return 0;
    }

    APS5_EXPORT("tIYf0W5VTi8", unknown_tIYf0W5VTi8_stub);
    int APS5_VABI unknown_tIYf0W5VTi8_stub(void) {
        NotImplemented_nid_no_patch("unknown_tIYf0W5VTi8_stub");
        return 0;
    }

    APS5_EXPORT("oARLr0ca9N8", unknown_oARLr0ca9N8_stub);
    int APS5_VABI unknown_oARLr0ca9N8_stub(void) {
        NotImplemented_nid_no_patch("unknown_oARLr0ca9N8_stub");
        return 0;
    }

    APS5_EXPORT("hdpVEUDFW3s", unknown_hdpVEUDFW3s_stub);
    int APS5_VABI unknown_hdpVEUDFW3s_stub(void) {
        NotImplemented_nid_no_patch("unknown_hdpVEUDFW3s_stub");
        return 0;
    }

    APS5_EXPORT("G3AnLNdRBjE", unknown_G3AnLNdRBjE_stub);
    int APS5_VABI unknown_G3AnLNdRBjE_stub(void) {
        NotImplemented_nid_no_patch("unknown_G3AnLNdRBjE_stub");
        return 0;
    }

    APS5_EXPORT("RQOqDbk3bSU", unknown_RQOqDbk3bSU_stub);
    int APS5_VABI unknown_RQOqDbk3bSU_stub(void) {
        NotImplemented_nid_no_patch("unknown_RQOqDbk3bSU_stub");
        return 0;
    }

    APS5_EXPORT("lU9YRFsgwSU", unknown_lU9YRFsgwSU_stub);
    int APS5_VABI unknown_lU9YRFsgwSU_stub(void) {
        NotImplemented_nid_no_patch("unknown_lU9YRFsgwSU_stub");
        return 0;
    }

    APS5_EXPORT("kLB5aGoUJXg", unknown_kLB5aGoUJXg_stub);
    int APS5_VABI unknown_kLB5aGoUJXg_stub(void) {
        NotImplemented_nid_no_patch("unknown_kLB5aGoUJXg_stub");
        return 0;
    }

    struct SceVideoOutBufferAttributeLegacy {
        uint32_t pixelFormat;
        uint32_t tilingMode;
        int32_t aspectRatio;
        uint32_t width;
        uint32_t height;
        uint32_t pitchInPixel;
        uint32_t option;
        uint32_t reserved0;
        uint64_t reserved1;
    };

    APS5_EXPORT("i6-sR91Wt-4", unknown_i6_sR91Wt_4_stub);
    void APS5_VABI unknown_i6_sR91Wt_4_stub(
        SceVideoOutBufferAttributeLegacy* attribute, 
        uint32_t pixelFormat,
        uint32_t tilingMode, 
        uint32_t aspectRatio, 
        uint32_t width,
        uint32_t height, 
        uint32_t pitchInPixel
    ) {
        if (!attribute) return;
        std::memset(attribute, 0, sizeof(*attribute));
        attribute->pixelFormat = pixelFormat;
        attribute->tilingMode = tilingMode;
        attribute->aspectRatio = aspectRatio;
        attribute->width = width;
        attribute->height = height;
        attribute->pitchInPixel = pitchInPixel;
        attribute->option = 0;
        std::printf("[AnyPS4 VideoOut] sceVideoOutSetBufferAttribute: %ux%u format=0x%08x tiling=%u pitch=%u\n",
                    width, height, pixelFormat, tilingMode, pitchInPixel);
        std::fflush(stdout);
    }

    APS5_EXPORT("w3BY+tAEiQY", unknown_w3BY_tAEiQY_stub);
    int APS5_VABI unknown_w3BY_tAEiQY_stub(
        int handle, 
        int startIndex, 
        void* const* addresses,
        int bufferNum, 
        const SceVideoOutBufferAttributeLegacy* attribute
    ) {
        std::printf("[AnyPS4 VideoOut] sceVideoOutRegisterBuffers: handle=%d startIndex=%d bufferNum=%d attr=%p\n",
                    handle, startIndex, bufferNum, (const void*)attribute);
        if (attribute) {
            std::printf("  size: %ux%u format=0x%08x tiling=%u pitch=%u\n",
                        attribute->width, attribute->height, attribute->pixelFormat, attribute->tilingMode, attribute->pitchInPixel);
        }
        if (addresses) {
            for (int i = 0; i < bufferNum; i++) {
                std::printf("  buffer[%d] = %p\n", i, addresses[i]);
            }
        }
        std::fflush(stdout);

#ifdef _WIN32
        using SceVideoOutRegisterBuffers2Fn = int (APS5_VABI *)(
            int handle, int setIndex, int bufferIndexStart, 
            const VideoOutBuffers* buffers, int bufferNum, 
            const VideoOutBufferAttribute2* attribute, int category, void* option
        );
        static SceVideoOutRegisterBuffers2Fn s_regBuffers2 = nullptr;
        static bool s_resolvedReg = false;
        if (!s_resolvedReg) {
            s_resolvedReg = true;
            HMODULE h = GetModuleHandleW(L"libSceVideoOut.prx");
            if (!h) h = LoadLibraryW(L"libs/libSceVideoOut.prx");
            if (!h) h = LoadLibraryW(L"libSceVideoOut.prx");
            if (h) {
                s_regBuffers2 = reinterpret_cast<SceVideoOutRegisterBuffers2Fn>(
                    reinterpret_cast<void*>(GetProcAddress(h, "rKBUtgRrtbk"))
                );
                if (!s_regBuffers2) {
                    s_regBuffers2 = reinterpret_cast<SceVideoOutRegisterBuffers2Fn>(
                        reinterpret_cast<void*>(GetProcAddress(h, "sceVideoOutRegisterBuffers2"))
                    );
                }
            }
            std::printf("[AnyPS4 VideoOut] Resolved sceVideoOutRegisterBuffers2 = %p\n", (void*)s_regBuffers2);
            std::fflush(stdout);
        }

        if (s_regBuffers2 && attribute && addresses) {
            VideoOutBufferAttribute2 attr2{};
            uint64_t format = attribute->pixelFormat;
            if ((format & 0xFFFFFFFF00000000ULL) == 0 && format != 0) {
                format = format << 32;
            }
            attr2.pixel_format = format;
            attr2.tiling_mode = attribute->tilingMode;
            attr2.aspect_ratio = 0;
            attr2.width = attribute->width;
            attr2.height = attribute->height;
            attr2.pitch_in_pixel = (attribute->tilingMode == 0) ? 0 : attribute->pitchInPixel;
            attr2.option = 0;

            std::vector<VideoOutBuffers> bufs(bufferNum);
            for (int i = 0; i < bufferNum; i++) {
                bufs[i].data = addresses[i];
                bufs[i].metadata = nullptr;
                bufs[i].reserved[0] = nullptr;
                bufs[i].reserved[1] = nullptr;
            }
            try {
                int res = s_regBuffers2(handle, 0, startIndex, bufs.data(), bufferNum, &attr2, 0, nullptr);
                std::printf("[AnyPS4 VideoOut] sceVideoOutRegisterBuffers2 returned %d\n", res);
                std::fflush(stdout);
                return res;
            } catch (const std::exception& e) {
                std::printf("[AnyPS4 VideoOut] sceVideoOutRegisterBuffers2 threw: %s\n", e.what());
                std::fflush(stdout);
                return 0;
            }
        }
#endif
        return 0;
    }

    APS5_EXPORT("GWnWQNXZH5M", unknown_GWnWQNXZH5M_stub);
    int APS5_VABI unknown_GWnWQNXZH5M_stub(void) {
        NotImplemented_nid_no_patch("unknown_GWnWQNXZH5M_stub");
        return 0;
    }

    APS5_EXPORT("gW8qyjYrUbk", unknown_gW8qyjYrUbk_stub);
    int APS5_VABI unknown_gW8qyjYrUbk_stub(void) {
        NotImplemented_nid_no_patch("unknown_gW8qyjYrUbk_stub");
        return 0;
    }

    APS5_EXPORT("K9tlODTQx3c", unknown_K9tlODTQx3c_stub);
    int APS5_VABI unknown_K9tlODTQx3c_stub(void) {
        NotImplemented_nid_no_patch("unknown_K9tlODTQx3c_stub");
        return 0;
    }

    APS5_EXPORT("dK8-SgYf6r4", unknown_dK8_SgYf6r4_stub);
    int APS5_VABI unknown_dK8_SgYf6r4_stub(void) {
        NotImplemented_nid_no_patch("unknown_dK8_SgYf6r4_stub");
        return 0;
    }

    APS5_EXPORT("MA9vSt7JImY", unknown_MA9vSt7JImY_stub);
    int APS5_VABI unknown_MA9vSt7JImY_stub(void) {
        NotImplemented_nid_no_patch("unknown_MA9vSt7JImY_stub");
        return 0;
    }

    APS5_EXPORT("8MqwVJd-cSY", unknown_8MqwVJd_cSY_stub);
    int APS5_VABI unknown_8MqwVJd_cSY_stub(void) {
        NotImplemented_nid_no_patch("unknown_8MqwVJd_cSY_stub");
        return 0;
    }

    APS5_EXPORT("-o8Vy6K2H-g", unknown__o8Vy6K2H_g_stub);
    int APS5_VABI unknown__o8Vy6K2H_g_stub(void) {
        NotImplemented_nid_no_patch("unknown__o8Vy6K2H_g_stub");
        return 0;
    }

    APS5_EXPORT("kRbUAm1Du+g", unknown_kRbUAm1Du_g_stub);
    int APS5_VABI unknown_kRbUAm1Du_g_stub(void) {
        NotImplemented_nid_no_patch("unknown_kRbUAm1Du_g_stub");
        return 0;
    }

    APS5_EXPORT("5-UHpg8s00I", unknown_5_UHpg8s00I_stub);
    int APS5_VABI unknown_5_UHpg8s00I_stub(void) {
        NotImplemented_nid_no_patch("unknown_5_UHpg8s00I_stub");
        return 0;
    }

    APS5_EXPORT("ZzkCpCDDeIE", unknown_ZzkCpCDDeIE_stub);
    int APS5_VABI unknown_ZzkCpCDDeIE_stub(void) {
        NotImplemented_nid_no_patch("unknown_ZzkCpCDDeIE_stub");
        return 0;
    }

    APS5_EXPORT("6hUKoSNxGHM", unknown_6hUKoSNxGHM_stub);
    int APS5_VABI unknown_6hUKoSNxGHM_stub(void) {
        NotImplemented_nid_no_patch("unknown_6hUKoSNxGHM_stub");
        return 0;
    }

    APS5_EXPORT("ApblR7nulzY", unknown_ApblR7nulzY_stub);
    int APS5_VABI unknown_ApblR7nulzY_stub(void) {
        NotImplemented_nid_no_patch("unknown_ApblR7nulzY_stub");
        return 0;
    }

    APS5_EXPORT("2YcKd7nB+Ag", unknown_2YcKd7nB_Ag_stub);
    int APS5_VABI unknown_2YcKd7nB_Ag_stub(void) {
        NotImplemented_nid_no_patch("unknown_2YcKd7nB_Ag_stub");
        return 0;
    }

    APS5_EXPORT("JRL5HQ04IFM", unknown_JRL5HQ04IFM_stub);
    int APS5_VABI unknown_JRL5HQ04IFM_stub(void) {
        NotImplemented_nid_no_patch("unknown_JRL5HQ04IFM_stub");
        return 0;
    }

    APS5_EXPORT("ALj-caXHUZI", unknown_ALj_caXHUZI_stub);
    int APS5_VABI unknown_ALj_caXHUZI_stub(void) {
        NotImplemented_nid_no_patch("unknown_ALj_caXHUZI_stub");
        return 0;
    }

    APS5_EXPORT("hqynGeY-OR8", unknown_hqynGeY_OR8_stub);
    int APS5_VABI unknown_hqynGeY_OR8_stub(void) {
        NotImplemented_nid_no_patch("unknown_hqynGeY_OR8_stub");
        return 0;
    }

    APS5_EXPORT("leypPkXymaA", unknown_leypPkXymaA_stub);
    int APS5_VABI unknown_leypPkXymaA_stub(void) {
        NotImplemented_nid_no_patch("unknown_leypPkXymaA_stub");
        return 0;
    }

    APS5_EXPORT("ngZMooSt-ys", unknown_ngZMooSt_ys_stub);
    int APS5_VABI unknown_ngZMooSt_ys_stub(void) {
        NotImplemented_nid_no_patch("unknown_ngZMooSt_ys_stub");
        return 0;
    }

    APS5_EXPORT("30Zxe35LtBg", unknown_30Zxe35LtBg_stub);
    int APS5_VABI unknown_30Zxe35LtBg_stub(void) {
        NotImplemented_nid_no_patch("unknown_30Zxe35LtBg_stub");
        return 0;
    }

    APS5_EXPORT("s+0pSDvfJkk", unknown_s_0pSDvfJkk_stub);
    int APS5_VABI unknown_s_0pSDvfJkk_stub(void) {
        NotImplemented_nid_no_patch("unknown_s_0pSDvfJkk_stub");
        return 0;
    }

    APS5_EXPORT("zGaiJod9Vic", unknown_zGaiJod9Vic_stub);
    int APS5_VABI unknown_zGaiJod9Vic_stub(void) {
        NotImplemented_nid_no_patch("unknown_zGaiJod9Vic_stub");
        return 0;
    }

    APS5_EXPORT("Nz-ZE7ur32I", unknown_Nz_ZE7ur32I_stub);
    int APS5_VABI unknown_Nz_ZE7ur32I_stub(void) {
        NotImplemented_nid_no_patch("unknown_Nz_ZE7ur32I_stub");
        return 0;
    }

    APS5_EXPORT("mtqDK9zkoIE", unknown_mtqDK9zkoIE_stub);
    int APS5_VABI unknown_mtqDK9zkoIE_stub(void) {
        NotImplemented_nid_no_patch("unknown_mtqDK9zkoIE_stub");
        return 0;
    }

    APS5_EXPORT("d2yn9y60yEU", unknown_d2yn9y60yEU_stub);
    int APS5_VABI unknown_d2yn9y60yEU_stub(void) {
        NotImplemented_nid_no_patch("unknown_d2yn9y60yEU_stub");
        return 0;
    }

    APS5_EXPORT("GXbL5lvDALs", unknown_GXbL5lvDALs_stub);
    int APS5_VABI unknown_GXbL5lvDALs_stub(void) {
        NotImplemented_nid_no_patch("unknown_GXbL5lvDALs_stub");
        return 0;
    }

    APS5_EXPORT("xYN7D+8y-KA", unknown_xYN7D_8y_KA_stub);
    int APS5_VABI unknown_xYN7D_8y_KA_stub(void) {
        NotImplemented_nid_no_patch("unknown_xYN7D_8y_KA_stub");
        return 0;
    }

    APS5_EXPORT("p+2EnxmaAMM", unknown_p_2EnxmaAMM_stub);
    int APS5_VABI unknown_p_2EnxmaAMM_stub(void) {
        NotImplemented_nid_no_patch("unknown_p_2EnxmaAMM_stub");
        return 0;
    }

    APS5_EXPORT("0UMeWRGnZKA", unknown_0UMeWRGnZKA_stub);
    int APS5_VABI unknown_0UMeWRGnZKA_stub(void) {
        NotImplemented_nid_no_patch("unknown_0UMeWRGnZKA_stub");
        return 0;
    }

    APS5_EXPORT("7vjNQ6Z1op0", unknown_7vjNQ6Z1op0_stub);
    int APS5_VABI unknown_7vjNQ6Z1op0_stub(void) {
        NotImplemented_nid_no_patch("unknown_7vjNQ6Z1op0_stub");
        return 0;
    }

    APS5_EXPORT("tHD5FPFXtu4", unknown_tHD5FPFXtu4_stub);
    int APS5_VABI unknown_tHD5FPFXtu4_stub(void) {
        NotImplemented_nid_no_patch("unknown_tHD5FPFXtu4_stub");
        return 0;
    }

    APS5_EXPORT("nNeC3F8-g+4", unknown_nNeC3F8_g_4_stub);
    int APS5_VABI unknown_nNeC3F8_g_4_stub(void) {
        NotImplemented_nid_no_patch("unknown_nNeC3F8_g_4_stub");
        return 0;
    }

    APS5_EXPORT("-f6M4caNe8k", unknown__f6M4caNe8k_stub);
    int APS5_VABI unknown__f6M4caNe8k_stub(void) {
        NotImplemented_nid_no_patch("unknown__f6M4caNe8k_stub");
        return 0;
    }

    APS5_EXPORT("10t3e5+JPnU", unknown_10t3e5_JPnU_stub);
    int APS5_VABI unknown_10t3e5_JPnU_stub(void) {
        NotImplemented_nid_no_patch("unknown_10t3e5_JPnU_stub");
        return 0;
    }

    APS5_EXPORT("fQQfP87I7hs", unknown_fQQfP87I7hs_stub);
    int APS5_VABI unknown_fQQfP87I7hs_stub(void) {
        NotImplemented_nid_no_patch("unknown_fQQfP87I7hs_stub");
        return 0;
    }

    APS5_EXPORT("ajvzc8e2upo", unknown_ajvzc8e2upo_stub);
    int APS5_VABI unknown_ajvzc8e2upo_stub(void) {
        NotImplemented_nid_no_patch("unknown_ajvzc8e2upo_stub");
        return 0;
    }

    APS5_EXPORT("vT9xhqPO6+0", unknown_vT9xhqPO6_0_stub);
    int APS5_VABI unknown_vT9xhqPO6_0_stub(void) {
        NotImplemented_nid_no_patch("unknown_vT9xhqPO6_0_stub");
        return 0;
    }

    APS5_EXPORT("q7GK98-nYSE", unknown_q7GK98_nYSE_stub);
    int APS5_VABI unknown_q7GK98_nYSE_stub(void) {
        NotImplemented_nid_no_patch("unknown_q7GK98_nYSE_stub");
        return 0;
    }

    APS5_EXPORT("9NwVTF2r-To", unknown_9NwVTF2r_To_stub);
    int APS5_VABI unknown_9NwVTF2r_To_stub(void) {
        NotImplemented_nid_no_patch("unknown_9NwVTF2r_To_stub");
        return 0;
    }

    APS5_EXPORT("AGYntkLfXCc", unknown_AGYntkLfXCc_stub);
    int APS5_VABI unknown_AGYntkLfXCc_stub(void) {
        NotImplemented_nid_no_patch("unknown_AGYntkLfXCc_stub");
        return 0;
    }

    APS5_EXPORT("ir5wHm8t4yQ", unknown_ir5wHm8t4yQ_stub);
    int APS5_VABI unknown_ir5wHm8t4yQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_ir5wHm8t4yQ_stub");
        return 0;
    }

    APS5_EXPORT("V6KSpKv9XJE", unknown_V6KSpKv9XJE_stub);
    int APS5_VABI unknown_V6KSpKv9XJE_stub(void) {
        NotImplemented_nid_no_patch("unknown_V6KSpKv9XJE_stub");
        return 0;
    }

    APS5_EXPORT("dMQ+xGvTdqM", unknown_dMQ_xGvTdqM_stub);
    int APS5_VABI unknown_dMQ_xGvTdqM_stub(void) {
        NotImplemented_nid_no_patch("unknown_dMQ_xGvTdqM_stub");
        return 0;
    }

    APS5_EXPORT("wUmwXZHaX1w", unknown_wUmwXZHaX1w_stub);
    int APS5_VABI unknown_wUmwXZHaX1w_stub(void) {
        NotImplemented_nid_no_patch("unknown_wUmwXZHaX1w_stub");
        return 0;
    }

    APS5_EXPORT("VqZX7POg2Mk", unknown_VqZX7POg2Mk_stub);
    int APS5_VABI unknown_VqZX7POg2Mk_stub(void) {
        NotImplemented_nid_no_patch("unknown_VqZX7POg2Mk_stub");
        return 0;
    }

    APS5_EXPORT("gQ6cUriNpgs", unknown_gQ6cUriNpgs_stub);
    int APS5_VABI unknown_gQ6cUriNpgs_stub(void) {
        NotImplemented_nid_no_patch("unknown_gQ6cUriNpgs_stub");
        return 0;
    }

    APS5_EXPORT("BD6kfx442Do", unknown_BD6kfx442Do_stub);
    int APS5_VABI unknown_BD6kfx442Do_stub(void) {
        NotImplemented_nid_no_patch("unknown_BD6kfx442Do_stub");
        return 0;
    }

    APS5_EXPORT("S9D8JSYIrjE", unknown_S9D8JSYIrjE_stub);
    int APS5_VABI unknown_S9D8JSYIrjE_stub(void) {
        NotImplemented_nid_no_patch("unknown_S9D8JSYIrjE_stub");
        return 0;
    }

    APS5_EXPORT("SX9IOde7tLo", unknown_SX9IOde7tLo_stub);
    int APS5_VABI unknown_SX9IOde7tLo_stub(void) {
        NotImplemented_nid_no_patch("unknown_SX9IOde7tLo_stub");
        return 0;
    }

    APS5_EXPORT("omVg1AdJGYQ", unknown_omVg1AdJGYQ_stub);
    int APS5_VABI unknown_omVg1AdJGYQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_omVg1AdJGYQ_stub");
        return 0;
    }

    APS5_EXPORT("cmvr0mOCX2Q", unknown_cmvr0mOCX2Q_stub);
    int APS5_VABI unknown_cmvr0mOCX2Q_stub(void) {
        NotImplemented_nid_no_patch("unknown_cmvr0mOCX2Q_stub");
        return 0;
    }

    APS5_EXPORT("iaGdIXzjp80", unknown_iaGdIXzjp80_stub);
    int APS5_VABI unknown_iaGdIXzjp80_stub(void) {
        NotImplemented_nid_no_patch("unknown_iaGdIXzjp80_stub");
        return 0;
    }

    APS5_EXPORT("XvA5KS56wcs", unknown_XvA5KS56wcs_stub);
    int APS5_VABI unknown_XvA5KS56wcs_stub(void) {
        NotImplemented_nid_no_patch("unknown_XvA5KS56wcs_stub");
        return 0;
    }

    APS5_EXPORT("sAxbHhAWMXM", unknown_sAxbHhAWMXM_stub);
    int APS5_VABI unknown_sAxbHhAWMXM_stub(void) {
        NotImplemented_nid_no_patch("unknown_sAxbHhAWMXM_stub");
        return 0;
    }

    APS5_EXPORT("9+g9iOq+7kg", unknown_9_g9iOq_7kg_stub);
    int APS5_VABI unknown_9_g9iOq_7kg_stub(void) {
        NotImplemented_nid_no_patch("unknown_9_g9iOq_7kg_stub");
        return 0;
    }

    APS5_EXPORT("WuuUhuKOxwQ", unknown_WuuUhuKOxwQ_stub);
    int APS5_VABI unknown_WuuUhuKOxwQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_WuuUhuKOxwQ_stub");
        return 0;
    }

    APS5_EXPORT("B6HVJtDYxEE", unknown_B6HVJtDYxEE_stub);
    int APS5_VABI unknown_B6HVJtDYxEE_stub(void) {
        NotImplemented_nid_no_patch("unknown_B6HVJtDYxEE_stub");
        return 0;
    }

    APS5_EXPORT("9GMinneGvk0", unknown_9GMinneGvk0_stub);
    int APS5_VABI unknown_9GMinneGvk0_stub(void) {
        NotImplemented_nid_no_patch("unknown_9GMinneGvk0_stub");
        return 0;
    }

    APS5_EXPORT("b9IYAN2rhlo", unknown_b9IYAN2rhlo_stub);
    int APS5_VABI unknown_b9IYAN2rhlo_stub(void) {
        NotImplemented_nid_no_patch("unknown_b9IYAN2rhlo_stub");
        return 0;
    }

    APS5_EXPORT("X8uNKyVpR1I", unknown_X8uNKyVpR1I_stub);
    int APS5_VABI unknown_X8uNKyVpR1I_stub(void) {
        NotImplemented_nid_no_patch("unknown_X8uNKyVpR1I_stub");
        return 0;
    }

    APS5_EXPORT("va+mHDV+Lwo", unknown_va_mHDV_Lwo_stub);
    int APS5_VABI unknown_va_mHDV_Lwo_stub(void) {
        NotImplemented_nid_no_patch("unknown_va_mHDV_Lwo_stub");
        return 0;
    }

    APS5_EXPORT("mIinAn8TvdY", unknown_mIinAn8TvdY_stub);
    int APS5_VABI unknown_mIinAn8TvdY_stub(void) {
        NotImplemented_nid_no_patch("unknown_mIinAn8TvdY_stub");
        return 0;
    }

    APS5_EXPORT("1yzPk-TN1+0", unknown_1yzPk_TN1_0_stub);
    int APS5_VABI unknown_1yzPk_TN1_0_stub(void) {
        NotImplemented_nid_no_patch("unknown_1yzPk_TN1_0_stub");
        return 0;
    }

    APS5_EXPORT("VFvyuEBlp+A", unknown_VFvyuEBlp_A_stub);
    int APS5_VABI unknown_VFvyuEBlp_A_stub(void) {
        NotImplemented_nid_no_patch("unknown_VFvyuEBlp_A_stub");
        return 0;
    }

    APS5_EXPORT("lgACxYBCgFw", unknown_lgACxYBCgFw_stub);
    int APS5_VABI unknown_lgACxYBCgFw_stub(void) {
        NotImplemented_nid_no_patch("unknown_lgACxYBCgFw_stub");
        return 0;
    }

    APS5_EXPORT("X17DF4uF7Co", unknown_X17DF4uF7Co_stub);
    int APS5_VABI unknown_X17DF4uF7Co_stub(void) {
        NotImplemented_nid_no_patch("unknown_X17DF4uF7Co_stub");
        return 0;
    }

    APS5_EXPORT("tlpXm5KLgqk", unknown_tlpXm5KLgqk_stub);
    int APS5_VABI unknown_tlpXm5KLgqk_stub(void) {
        NotImplemented_nid_no_patch("unknown_tlpXm5KLgqk_stub");
        return 0;
    }

    APS5_EXPORT("LhCPctIICxQ", unknown_LhCPctIICxQ_stub);
    int APS5_VABI unknown_LhCPctIICxQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_LhCPctIICxQ_stub");
        return 0;
    }

    APS5_EXPORT("rJNPJqDCpiI", unknown_rJNPJqDCpiI_stub);
    int APS5_VABI unknown_rJNPJqDCpiI_stub(void) {
        NotImplemented_nid_no_patch("unknown_rJNPJqDCpiI_stub");
        return 0;
    }

    APS5_EXPORT("vbh-MWtjMh4", unknown_vbh_MWtjMh4_stub);
    int APS5_VABI unknown_vbh_MWtjMh4_stub(void) {
        NotImplemented_nid_no_patch("unknown_vbh_MWtjMh4_stub");
        return 0;
    }

    APS5_EXPORT("LLdnqVnnNBQ", unknown_LLdnqVnnNBQ_stub);
    int APS5_VABI unknown_LLdnqVnnNBQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_LLdnqVnnNBQ_stub");
        return 0;
    }

    APS5_EXPORT("-bAjEe-hdCg", unknown__bAjEe_hdCg_stub);
    int APS5_VABI unknown__bAjEe_hdCg_stub(void) {
        NotImplemented_nid_no_patch("unknown__bAjEe_hdCg_stub");
        return 0;
    }

    APS5_EXPORT("s0u30pOfi9Q", unknown_s0u30pOfi9Q_stub);
    int APS5_VABI unknown_s0u30pOfi9Q_stub(void) {
        NotImplemented_nid_no_patch("unknown_s0u30pOfi9Q_stub");
        return 0;
    }

    APS5_EXPORT("IcuECtP3L0E", unknown_IcuECtP3L0E_stub);
    int APS5_VABI unknown_IcuECtP3L0E_stub(void) {
        NotImplemented_nid_no_patch("unknown_IcuECtP3L0E_stub");
        return 0;
    }

    APS5_EXPORT("vycUuYWwilI", unknown_vycUuYWwilI_stub);
    int APS5_VABI unknown_vycUuYWwilI_stub(void) {
        NotImplemented_nid_no_patch("unknown_vycUuYWwilI_stub");
        return 0;
    }

    APS5_EXPORT("8Z2Jc5GvGDI", unknown_8Z2Jc5GvGDI_stub);
    int APS5_VABI unknown_8Z2Jc5GvGDI_stub(void) {
        NotImplemented_nid_no_patch("unknown_8Z2Jc5GvGDI_stub");
        return 0;
    }

    APS5_EXPORT("zk6c65xoyO0", unknown_zk6c65xoyO0_stub);
    int APS5_VABI unknown_zk6c65xoyO0_stub(void) {
        NotImplemented_nid_no_patch("unknown_zk6c65xoyO0_stub");
        return 0;
    }

    APS5_EXPORT("r6MyYJkryz8", unknown_r6MyYJkryz8_stub);
    int APS5_VABI unknown_r6MyYJkryz8_stub(void) {
        NotImplemented_nid_no_patch("unknown_r6MyYJkryz8_stub");
        return 0;
    }

    APS5_EXPORT("Gaxrp3EWY-M", unknown_Gaxrp3EWY_M_stub);
    int APS5_VABI unknown_Gaxrp3EWY_M_stub(void) {
        NotImplemented_nid_no_patch("unknown_Gaxrp3EWY_M_stub");
        return 0;
    }

    APS5_EXPORT("8b2o8RfK620", unknown_8b2o8RfK620_stub);
    int APS5_VABI unknown_8b2o8RfK620_stub(void) {
        NotImplemented_nid_no_patch("unknown_8b2o8RfK620_stub");
        return 0;
    }

    APS5_EXPORT("hks1Z-mbivM", unknown_hks1Z_mbivM_stub);
    int APS5_VABI unknown_hks1Z_mbivM_stub(void) {
        NotImplemented_nid_no_patch("unknown_hks1Z_mbivM_stub");
        return 0;
    }

    APS5_EXPORT("9G7fpmodu1Q", unknown_9G7fpmodu1Q_stub);
    int APS5_VABI unknown_9G7fpmodu1Q_stub(void) {
        NotImplemented_nid_no_patch("unknown_9G7fpmodu1Q_stub");
        return 0;
    }

    APS5_EXPORT("yl2jH6kx6VY", unknown_yl2jH6kx6VY_stub);
    int APS5_VABI unknown_yl2jH6kx6VY_stub(void) {
        NotImplemented_nid_no_patch("unknown_yl2jH6kx6VY_stub");
        return 0;
    }

    APS5_EXPORT("nrvHUJnoOGM", unknown_nrvHUJnoOGM_stub);
    int APS5_VABI unknown_nrvHUJnoOGM_stub(void) {
        NotImplemented_nid_no_patch("unknown_nrvHUJnoOGM_stub");
        return 0;
    }

    APS5_EXPORT("xotzrkLV-aU", unknown_xotzrkLV_aU_stub);
    int APS5_VABI unknown_xotzrkLV_aU_stub(void) {
        NotImplemented_nid_no_patch("unknown_xotzrkLV_aU_stub");
        return 0;
    }

    APS5_EXPORT("VFM4TzMTUPI", unknown_VFM4TzMTUPI_stub);
    int APS5_VABI unknown_VFM4TzMTUPI_stub(void) {
        NotImplemented_nid_no_patch("unknown_VFM4TzMTUPI_stub");
        return 0;
    }

    APS5_EXPORT("FbtukaCjFCM", unknown_FbtukaCjFCM_stub);
    int APS5_VABI unknown_FbtukaCjFCM_stub(void) {
        NotImplemented_nid_no_patch("unknown_FbtukaCjFCM_stub");
        return 0;
    }

    APS5_EXPORT("kyyI+gLshKQ", unknown_kyyI_gLshKQ_stub);
    int APS5_VABI unknown_kyyI_gLshKQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_kyyI_gLshKQ_stub");
        return 0;
    }

    APS5_EXPORT("0+LtsbPVpt8", unknown_0_LtsbPVpt8_stub);
    int APS5_VABI unknown_0_LtsbPVpt8_stub(void) {
        NotImplemented_nid_no_patch("unknown_0_LtsbPVpt8_stub");
        return 0;
    }

    APS5_EXPORT("sZ8FuTrbhUc", unknown_sZ8FuTrbhUc_stub);
    int APS5_VABI unknown_sZ8FuTrbhUc_stub(void) {
        NotImplemented_nid_no_patch("unknown_sZ8FuTrbhUc_stub");
        return 0;
    }

    APS5_EXPORT("K0gxiS+SBho", unknown_K0gxiS_SBho_stub);
    int APS5_VABI unknown_K0gxiS_SBho_stub(void) {
        NotImplemented_nid_no_patch("unknown_K0gxiS_SBho_stub");
        return 0;
    }

    APS5_EXPORT("7IHg-sW3Ez8", unknown_7IHg_sW3Ez8_stub);
    int APS5_VABI unknown_7IHg_sW3Ez8_stub(void) {
        NotImplemented_nid_no_patch("unknown_7IHg_sW3Ez8_stub");
        return 0;
    }

    APS5_EXPORT("BNYc2zKvxyM", unknown_BNYc2zKvxyM_stub);
    int APS5_VABI unknown_BNYc2zKvxyM_stub(void) {
        NotImplemented_nid_no_patch("unknown_BNYc2zKvxyM_stub");
        return 0;
    }

    APS5_EXPORT("V4EVrruHuy8", unknown_V4EVrruHuy8_stub);
    int APS5_VABI unknown_V4EVrruHuy8_stub(void) {
        NotImplemented_nid_no_patch("unknown_V4EVrruHuy8_stub");
        return 0;
    }

    APS5_EXPORT("wLaxchvEEnk", unknown_wLaxchvEEnk_stub);
    int APS5_VABI unknown_wLaxchvEEnk_stub(void) {
        NotImplemented_nid_no_patch("unknown_wLaxchvEEnk_stub");
        return 0;
    }

    APS5_EXPORT("-p97-goGFC4", unknown__p97_goGFC4_stub);
    int APS5_VABI unknown__p97_goGFC4_stub(void) {
        NotImplemented_nid_no_patch("unknown__p97_goGFC4_stub");
        return 0;
    }

    APS5_EXPORT("owxYieafJSM", unknown_owxYieafJSM_stub);
    int APS5_VABI unknown_owxYieafJSM_stub(void) {
        NotImplemented_nid_no_patch("unknown_owxYieafJSM_stub");
        return 0;
    }

    APS5_EXPORT("a0+h8BwDUUA", unknown_a0_h8BwDUUA_stub);
    int APS5_VABI unknown_a0_h8BwDUUA_stub(void) {
        NotImplemented_nid_no_patch("unknown_a0_h8BwDUUA_stub");
        return 0;
    }

    APS5_EXPORT("YYs7Nb1n3rM", unknown_YYs7Nb1n3rM_stub);
    int APS5_VABI unknown_YYs7Nb1n3rM_stub(void) {
        NotImplemented_nid_no_patch("unknown_YYs7Nb1n3rM_stub");
        return 0;
    }

    APS5_EXPORT("6p9jvljuvsw", unknown_6p9jvljuvsw_stub);
    int APS5_VABI unknown_6p9jvljuvsw_stub(void) {
        NotImplemented_nid_no_patch("unknown_6p9jvljuvsw_stub");
        return 0;
    }

    APS5_EXPORT("iCq5xW5KQW4", unknown_iCq5xW5KQW4_stub);
    int APS5_VABI unknown_iCq5xW5KQW4_stub(void) {
        NotImplemented_nid_no_patch("unknown_iCq5xW5KQW4_stub");
        return 0;
    }

    APS5_EXPORT("Jj4mkpFO2gE", unknown_Jj4mkpFO2gE_stub);
    int APS5_VABI unknown_Jj4mkpFO2gE_stub(void) {
        NotImplemented_nid_no_patch("unknown_Jj4mkpFO2gE_stub");
        return 0;
    }

    APS5_EXPORT("PYFS1H70bDs", unknown_PYFS1H70bDs_stub);
    int APS5_VABI unknown_PYFS1H70bDs_stub(void) {
        NotImplemented_nid_no_patch("unknown_PYFS1H70bDs_stub");
        return 0;
    }

    APS5_EXPORT("XTWR0UXvcgs", unknown_XTWR0UXvcgs_stub);
    int APS5_VABI unknown_XTWR0UXvcgs_stub(void) {
        NotImplemented_nid_no_patch("unknown_XTWR0UXvcgs_stub");
        return 0;
    }

    APS5_EXPORT("31Bh5lfPPXs", unknown_31Bh5lfPPXs_stub);
    int APS5_VABI unknown_31Bh5lfPPXs_stub(void) {
        NotImplemented_nid_no_patch("unknown_31Bh5lfPPXs_stub");
        return 0;
    }

    APS5_EXPORT("Kv8XXD7X7XQ", unknown_Kv8XXD7X7XQ_stub);
    int APS5_VABI unknown_Kv8XXD7X7XQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_Kv8XXD7X7XQ_stub");
        return 0;
    }

    APS5_EXPORT("o2PhQ4mUZuE", unknown_o2PhQ4mUZuE_stub);
    int APS5_VABI unknown_o2PhQ4mUZuE_stub(void) {
        NotImplemented_nid_no_patch("unknown_o2PhQ4mUZuE_stub");
        return 0;
    }

    APS5_EXPORT("6esKXS17kNM", unknown_6esKXS17kNM_stub);
    int APS5_VABI unknown_6esKXS17kNM_stub(void) {
        NotImplemented_nid_no_patch("unknown_6esKXS17kNM_stub");
        return 0;
    }

    APS5_EXPORT("YlpnKm99h3Q", unknown_YlpnKm99h3Q_stub);
    int APS5_VABI unknown_YlpnKm99h3Q_stub(void) {
        NotImplemented_nid_no_patch("unknown_YlpnKm99h3Q_stub");
        return 0;
    }

    APS5_EXPORT("q-uIM1VNvwg", unknown_q_uIM1VNvwg_stub);
    int APS5_VABI unknown_q_uIM1VNvwg_stub(void) {
        NotImplemented_nid_no_patch("unknown_q_uIM1VNvwg_stub");
        return 0;
    }

    APS5_EXPORT("CQtPRSF6Ds8", unknown_CQtPRSF6Ds8_stub);
    int APS5_VABI unknown_CQtPRSF6Ds8_stub(void) {
        NotImplemented_nid_no_patch("unknown_CQtPRSF6Ds8_stub");
        return 0;
    }

    APS5_EXPORT("rdgs5Z1MyFw", unknown_rdgs5Z1MyFw_stub);
    int APS5_VABI unknown_rdgs5Z1MyFw_stub(void) {
        NotImplemented_nid_no_patch("unknown_rdgs5Z1MyFw_stub");
        return 0;
    }

    APS5_EXPORT("KjNeZ-29ysQ", unknown_KjNeZ_29ysQ_stub);
    int APS5_VABI unknown_KjNeZ_29ysQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_KjNeZ_29ysQ_stub");
        return 0;
    }

    APS5_EXPORT("XUjdsSTTZ3U", unknown_XUjdsSTTZ3U_stub);
    int APS5_VABI unknown_XUjdsSTTZ3U_stub(void) {
        NotImplemented_nid_no_patch("unknown_XUjdsSTTZ3U_stub");
        return 0;
    }

    APS5_EXPORT("noQgleu+KLE", unknown_noQgleu_KLE_stub);
    int APS5_VABI unknown_noQgleu_KLE_stub(void) {
        NotImplemented_nid_no_patch("unknown_noQgleu_KLE_stub");
        return 0;
    }

    APS5_EXPORT("XbkjbobZlCY", unknown_XbkjbobZlCY_stub);
    int APS5_VABI unknown_XbkjbobZlCY_stub(void) {
        NotImplemented_nid_no_patch("unknown_XbkjbobZlCY_stub");
        return 0;
    }

    APS5_EXPORT("q7U6tEAQf7c", unknown_q7U6tEAQf7c_stub);
    int APS5_VABI unknown_q7U6tEAQf7c_stub(void) {
        NotImplemented_nid_no_patch("unknown_q7U6tEAQf7c_stub");
        return 0;
    }

    APS5_EXPORT("TJCAxto9SEU", unknown_TJCAxto9SEU_stub);
    int APS5_VABI unknown_TJCAxto9SEU_stub(void) {
        NotImplemented_nid_no_patch("unknown_TJCAxto9SEU_stub");
        return 0;
    }

    APS5_EXPORT("GNcF4oidY0Y", unknown_GNcF4oidY0Y_stub);
    int APS5_VABI unknown_GNcF4oidY0Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_GNcF4oidY0Y_stub");
        return 0;
    }

    APS5_EXPORT("28xmRUFao68", unknown_28xmRUFao68_stub);
    int APS5_VABI unknown_28xmRUFao68_stub(void) {
        NotImplemented_nid_no_patch("unknown_28xmRUFao68_stub");
        return 0;
    }

    APS5_EXPORT("LHuSmO3SLd8", unknown_LHuSmO3SLd8_stub);
    int APS5_VABI unknown_LHuSmO3SLd8_stub(void) {
        NotImplemented_nid_no_patch("unknown_LHuSmO3SLd8_stub");
        return 0;
    }

    APS5_EXPORT("zuftnZ9BD9w", unknown_zuftnZ9BD9w_stub);
    int APS5_VABI unknown_zuftnZ9BD9w_stub(void) {
        NotImplemented_nid_no_patch("unknown_zuftnZ9BD9w_stub");
        return 0;
    }

    APS5_EXPORT("6ClJwE3AiGs", unknown_6ClJwE3AiGs_stub);
    int APS5_VABI unknown_6ClJwE3AiGs_stub(void) {
        NotImplemented_nid_no_patch("unknown_6ClJwE3AiGs_stub");
        return 0;
    }

    APS5_EXPORT("7ONbnvN2brw", unknown_7ONbnvN2brw_stub);
    int APS5_VABI unknown_7ONbnvN2brw_stub(void) {
        NotImplemented_nid_no_patch("unknown_7ONbnvN2brw_stub");
        return 0;
    }

    APS5_EXPORT("XaKJqdhjD88", unknown_XaKJqdhjD88_stub);
    int APS5_VABI unknown_XaKJqdhjD88_stub(void) {
        NotImplemented_nid_no_patch("unknown_XaKJqdhjD88_stub");
        return 0;
    }

    APS5_EXPORT("+9j+VbOE+xQ", unknown__9j_VbOE_xQ_stub);
    int APS5_VABI unknown__9j_VbOE_xQ_stub(void) {
        NotImplemented_nid_no_patch("unknown__9j_VbOE_xQ_stub");
        return 0;
    }

    APS5_EXPORT("NhyOMK5FxAk", unknown_NhyOMK5FxAk_stub);
    int APS5_VABI unknown_NhyOMK5FxAk_stub(void) {
        NotImplemented_nid_no_patch("unknown_NhyOMK5FxAk_stub");
        return 0;
    }

    APS5_EXPORT("Foc0YVGG9s8", unknown_Foc0YVGG9s8_stub);
    int APS5_VABI unknown_Foc0YVGG9s8_stub(void) {
        NotImplemented_nid_no_patch("unknown_Foc0YVGG9s8_stub");
        return 0;
    }

    APS5_EXPORT("6ZKsmn9DS0Y", unknown_6ZKsmn9DS0Y_stub);
    int APS5_VABI unknown_6ZKsmn9DS0Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_6ZKsmn9DS0Y_stub");
        return 0;
    }

    APS5_EXPORT("ZpzDxqY5Zcw", unknown_ZpzDxqY5Zcw_stub);
    int APS5_VABI unknown_ZpzDxqY5Zcw_stub(void) {
        NotImplemented_nid_no_patch("unknown_ZpzDxqY5Zcw_stub");
        return 0;
    }

    APS5_EXPORT("qc4pnagDrkQ", unknown_qc4pnagDrkQ_stub);
    int APS5_VABI unknown_qc4pnagDrkQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_qc4pnagDrkQ_stub");
        return 0;
    }

    APS5_EXPORT("iJEDK60-2p4", unknown_iJEDK60_2p4_stub);
    int APS5_VABI unknown_iJEDK60_2p4_stub(void) {
        NotImplemented_nid_no_patch("unknown_iJEDK60_2p4_stub");
        return 0;
    }

    APS5_EXPORT("cBzNNtt2-GU", unknown_cBzNNtt2_GU_stub);
    int APS5_VABI unknown_cBzNNtt2_GU_stub(void) {
        NotImplemented_nid_no_patch("unknown_cBzNNtt2_GU_stub");
        return 0;
    }

    APS5_EXPORT("gpSEllb2338", unknown_gpSEllb2338_stub);
    int APS5_VABI unknown_gpSEllb2338_stub(void) {
        NotImplemented_nid_no_patch("unknown_gpSEllb2338_stub");
        return 0;
    }

    APS5_EXPORT("evQPB2JiOTo", unknown_evQPB2JiOTo_stub);
    int APS5_VABI unknown_evQPB2JiOTo_stub(void) {
        NotImplemented_nid_no_patch("unknown_evQPB2JiOTo_stub");
        return 0;
    }

    APS5_EXPORT("i51FQZY--Sw", unknown_i51FQZY__Sw_stub);
    int APS5_VABI unknown_i51FQZY__Sw_stub(void) {
        NotImplemented_nid_no_patch("unknown_i51FQZY__Sw_stub");
        return 0;
    }

    APS5_EXPORT("jmiUcZi+ONI", unknown_jmiUcZi_ONI_stub);
    int APS5_VABI unknown_jmiUcZi_ONI_stub(void) {
        NotImplemented_nid_no_patch("unknown_jmiUcZi_ONI_stub");
        return 0;
    }

    APS5_EXPORT("3uIwm8ckbVc", unknown_3uIwm8ckbVc_stub);
    int APS5_VABI unknown_3uIwm8ckbVc_stub(void) {
        NotImplemented_nid_no_patch("unknown_3uIwm8ckbVc_stub");
        return 0;
    }

    APS5_EXPORT("mXJwKDDXQ3s", unknown_mXJwKDDXQ3s_stub);
    int APS5_VABI unknown_mXJwKDDXQ3s_stub(void) {
        NotImplemented_nid_no_patch("unknown_mXJwKDDXQ3s_stub");
        return 0;
    }

    APS5_EXPORT("F8luFJ2FEPY", unknown_F8luFJ2FEPY_stub);
    int APS5_VABI unknown_F8luFJ2FEPY_stub(void) {
        NotImplemented_nid_no_patch("unknown_F8luFJ2FEPY_stub");
        return 0;
    }

    APS5_EXPORT("IGc6FTBp6jE", unknown_IGc6FTBp6jE_stub);
    int APS5_VABI unknown_IGc6FTBp6jE_stub(void) {
        NotImplemented_nid_no_patch("unknown_IGc6FTBp6jE_stub");
        return 0;
    }

    APS5_EXPORT("9IKooW79-AM", unknown_9IKooW79_AM_stub);
    int APS5_VABI unknown_9IKooW79_AM_stub(void) {
        NotImplemented_nid_no_patch("unknown_9IKooW79_AM_stub");
        return 0;
    }

    APS5_EXPORT("usKbuvy2hQg", unknown_usKbuvy2hQg_stub);
    int APS5_VABI unknown_usKbuvy2hQg_stub(void) {
        NotImplemented_nid_no_patch("unknown_usKbuvy2hQg_stub");
        return 0;
    }

    APS5_EXPORT("b0xyllnVY-I", unknown_b0xyllnVY_I_stub);
    int APS5_VABI unknown_b0xyllnVY_I_stub(void) {
        NotImplemented_nid_no_patch("unknown_b0xyllnVY_I_stub");
        return 0;
    }

    APS5_EXPORT("Kx-h-nWQJ8A", unknown_Kx_h_nWQJ8A_stub);
    int APS5_VABI unknown_Kx_h_nWQJ8A_stub(void) {
        NotImplemented_nid_no_patch("unknown_Kx_h_nWQJ8A_stub");
        return 0;
    }

    APS5_EXPORT("b08AgtPlHPg", unknown_b08AgtPlHPg_stub);
    int APS5_VABI unknown_b08AgtPlHPg_stub(void) {
        NotImplemented_nid_no_patch("unknown_b08AgtPlHPg_stub");
        return 0;
    }

    APS5_EXPORT("ihxrbsoSKWc", unknown_ihxrbsoSKWc_stub);
    int APS5_VABI unknown_ihxrbsoSKWc_stub(void) {
        NotImplemented_nid_no_patch("unknown_ihxrbsoSKWc_stub");
        return 0;
    }

    APS5_EXPORT("X9Omw9dwv5M", unknown_X9Omw9dwv5M_stub);
    int APS5_VABI unknown_X9Omw9dwv5M_stub(void) {
        NotImplemented_nid_no_patch("unknown_X9Omw9dwv5M_stub");
        return 0;
    }

    APS5_EXPORT("ffrNQOshows", unknown_ffrNQOshows_stub);
    int APS5_VABI unknown_ffrNQOshows_stub(void) {
        NotImplemented_nid_no_patch("unknown_ffrNQOshows_stub");
        return 0;
    }

    APS5_EXPORT("EJapNl2+pgU", unknown_EJapNl2_pgU_stub);
    int APS5_VABI unknown_EJapNl2_pgU_stub(void) {
        NotImplemented_nid_no_patch("unknown_EJapNl2_pgU_stub");
        return 0;
    }

    APS5_EXPORT("5udAm+6boVg", unknown_5udAm_6boVg_stub);
    int APS5_VABI unknown_5udAm_6boVg_stub(void) {
        NotImplemented_nid_no_patch("unknown_5udAm_6boVg_stub");
        return 0;
    }

    APS5_EXPORT("qpGITzPE+Zc", unknown_qpGITzPE_Zc_stub);
    int APS5_VABI unknown_qpGITzPE_Zc_stub(void) {
        NotImplemented_nid_no_patch("unknown_qpGITzPE_Zc_stub");
        return 0;
    }

    APS5_EXPORT("+AFvOEXrKJk", unknown__AFvOEXrKJk_stub);
    int APS5_VABI unknown__AFvOEXrKJk_stub(void) {
        NotImplemented_nid_no_patch("unknown__AFvOEXrKJk_stub");
        return 0;
    }

    APS5_EXPORT("FUHG8sQ3R58", unknown_FUHG8sQ3R58_stub);
    int APS5_VABI unknown_FUHG8sQ3R58_stub(void) {
        NotImplemented_nid_no_patch("unknown_FUHG8sQ3R58_stub");
        return 0;
    }

    APS5_EXPORT("jtkqXpAOY6w", unknown_jtkqXpAOY6w_stub);
    int APS5_VABI unknown_jtkqXpAOY6w_stub(void) {
        NotImplemented_nid_no_patch("unknown_jtkqXpAOY6w_stub");
        return 0;
    }

    APS5_EXPORT("VJNjFtqiF5w", unknown_VJNjFtqiF5w_stub);
    int APS5_VABI unknown_VJNjFtqiF5w_stub(void) {
        NotImplemented_nid_no_patch("unknown_VJNjFtqiF5w_stub");
        return 0;
    }

    APS5_EXPORT("vckdzbQ46SI", unknown_vckdzbQ46SI_stub);
    int APS5_VABI unknown_vckdzbQ46SI_stub(void) {
        NotImplemented_nid_no_patch("unknown_vckdzbQ46SI_stub");
        return 0;
    }

    APS5_EXPORT("5uFKckiJYRM", unknown_5uFKckiJYRM_stub);
    int APS5_VABI unknown_5uFKckiJYRM_stub(void) {
        NotImplemented_nid_no_patch("unknown_5uFKckiJYRM_stub");
        return 0;
    }

    APS5_EXPORT("q-qhDxP67Hg", unknown_q_qhDxP67Hg_stub);
    int APS5_VABI unknown_q_qhDxP67Hg_stub(void) {
        NotImplemented_nid_no_patch("unknown_q_qhDxP67Hg_stub");
        return 0;
    }

    APS5_EXPORT("K3BKBBYKUSE", unknown_K3BKBBYKUSE_stub);
    int APS5_VABI unknown_K3BKBBYKUSE_stub(void) {
        NotImplemented_nid_no_patch("unknown_K3BKBBYKUSE_stub");
        return 0;
    }

    APS5_EXPORT("cFCp0NX8wf0", unknown_cFCp0NX8wf0_stub);
    int APS5_VABI unknown_cFCp0NX8wf0_stub(void) {
        NotImplemented_nid_no_patch("unknown_cFCp0NX8wf0_stub");
        return 0;
    }

    APS5_EXPORT("gAhCn6UiU4Y", unknown_gAhCn6UiU4Y_stub);
    int APS5_VABI unknown_gAhCn6UiU4Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_gAhCn6UiU4Y_stub");
        return 0;
    }

    APS5_EXPORT("XiyzNZ9J4nQ", unknown_XiyzNZ9J4nQ_stub);
    int APS5_VABI unknown_XiyzNZ9J4nQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_XiyzNZ9J4nQ_stub");
        return 0;
    }

    APS5_EXPORT("+xuDhxlWRPg", unknown__xuDhxlWRPg_stub);
    int APS5_VABI unknown__xuDhxlWRPg_stub(void) {
        NotImplemented_nid_no_patch("unknown__xuDhxlWRPg_stub");
        return 0;
    }

    APS5_EXPORT("zwY0YV91TTI", unknown_zwY0YV91TTI_stub);
    int APS5_VABI unknown_zwY0YV91TTI_stub(void) {
        NotImplemented_nid_no_patch("unknown_zwY0YV91TTI_stub");
        return 0;
    }

    APS5_EXPORT("xbxNatawohc", unknown_xbxNatawohc_stub);
    int APS5_VABI unknown_xbxNatawohc_stub(
        uint32_t count,
        uint32_t* dcb_gpu_addrs[],
        uint32_t* dcb_sizes_in_bytes,
        uint32_t* ccb_gpu_addrs[],
        uint32_t* ccb_sizes_in_bytes,
        uint32_t vo_handle,
        uint32_t buf_idx,
        uint32_t flip_mode,
        int64_t flip_arg
    ) {
        static int flip_counter = 0;
        if (flip_counter < 10 || (flip_counter % 300) == 0) {
            std::printf("[AnyPS4 GNM] sceGnmSubmitAndFlipCommandBuffers: count=%u, handle=%u, buf_idx=%u, mode=%u, flip_arg=%lld (flip #%d)\n",
                        count, vo_handle, buf_idx, flip_mode, (long long)flip_arg, flip_counter);
            std::fflush(stdout);
        }
        flip_counter++;

#ifdef _WIN32
        using SceVideoOutSubmitFlipFn = int (APS5_VABI *)(int handle, int index, int flipMode, int64_t flipArg);
        static SceVideoOutSubmitFlipFn s_submitFlip = nullptr;
        static bool s_resolved = false;
        if (!s_resolved) {
            s_resolved = true;
            HMODULE h = GetModuleHandleW(L"libSceVideoOut.prx");
            if (!h) h = LoadLibraryW(L"libs/libSceVideoOut.prx");
            if (!h) h = LoadLibraryW(L"libSceVideoOut.prx");
            if (h) {
                s_submitFlip = reinterpret_cast<SceVideoOutSubmitFlipFn>(
                    reinterpret_cast<void*>(GetProcAddress(h, "U46NwOiJpys"))
                );
                if (!s_submitFlip) {
                    s_submitFlip = reinterpret_cast<SceVideoOutSubmitFlipFn>(
                        reinterpret_cast<void*>(GetProcAddress(h, "sceVideoOutSubmitFlip"))
                    );
                }
            }
            std::printf("[AnyPS4 GNM] Resolved sceVideoOutSubmitFlip = %p\n", (void*)s_submitFlip);
            std::fflush(stdout);
        }
        if (s_submitFlip) {
            try {
                return s_submitFlip(static_cast<int>(vo_handle), static_cast<int>(buf_idx), static_cast<int>(flip_mode), flip_arg);
            } catch (const std::exception& e) {
                static bool logged_ex = false;
                if (!logged_ex) {
                    logged_ex = true;
                    std::printf("[AnyPS4 GNM] sceVideoOutSubmitFlip threw: %s (suppressing further)\n", e.what());
                    std::fflush(stdout);
                }
                return 0;
            }
        }
#endif
        return 0;
    }

    APS5_EXPORT("Ga6r7H6Y0RI", unknown_Ga6r7H6Y0RI_stub);
    int APS5_VABI unknown_Ga6r7H6Y0RI_stub(void) {
        NotImplemented_nid_no_patch("unknown_Ga6r7H6Y0RI_stub");
        return 0;
    }

    APS5_EXPORT("jRcI8VcgTz4", unknown_jRcI8VcgTz4_stub);
    int APS5_VABI unknown_jRcI8VcgTz4_stub(void) {
        NotImplemented_nid_no_patch("unknown_jRcI8VcgTz4_stub");
        return 0;
    }

    APS5_EXPORT("yvZ73uQUqrk", unknown_yvZ73uQUqrk_stub);
    int APS5_VABI unknown_yvZ73uQUqrk_stub(void) {
        NotImplemented_nid_no_patch("unknown_yvZ73uQUqrk_stub");
        return 0;
    }

    APS5_EXPORT("UJwNuMBcUAk", unknown_UJwNuMBcUAk_stub);
    int APS5_VABI unknown_UJwNuMBcUAk_stub(void) {
        NotImplemented_nid_no_patch("unknown_UJwNuMBcUAk_stub");
        return 0;
    }

    APS5_EXPORT("PVT+fuoS9gU", unknown_PVT_fuoS9gU_stub);
    int APS5_VABI unknown_PVT_fuoS9gU_stub(void) {
        NotImplemented_nid_no_patch("unknown_PVT_fuoS9gU_stub");
        return 0;
    }

    APS5_EXPORT("ArSg-TGinhk", unknown_ArSg_TGinhk_stub);
    int APS5_VABI unknown_ArSg_TGinhk_stub(void) {
        NotImplemented_nid_no_patch("unknown_ArSg_TGinhk_stub");
        return 0;
    }

    APS5_EXPORT("UtObDRQiGbs", unknown_UtObDRQiGbs_stub);
    int APS5_VABI unknown_UtObDRQiGbs_stub(void) {
        NotImplemented_nid_no_patch("unknown_UtObDRQiGbs_stub");
        return 0;
    }

    APS5_EXPORT("bX5IbRvECXk", unknown_bX5IbRvECXk_stub);
    int APS5_VABI unknown_bX5IbRvECXk_stub(void) {
        NotImplemented_nid_no_patch("unknown_bX5IbRvECXk_stub");
        return 0;
    }

    APS5_EXPORT("byXlqupd8cE", unknown_byXlqupd8cE_stub);
    int APS5_VABI unknown_byXlqupd8cE_stub(void) {
        NotImplemented_nid_no_patch("unknown_byXlqupd8cE_stub");
        return 0;
    }

    APS5_EXPORT("HHo1BAljZO8", unknown_HHo1BAljZO8_stub);
    int APS5_VABI unknown_HHo1BAljZO8_stub(void) {
        NotImplemented_nid_no_patch("unknown_HHo1BAljZO8_stub");
        return 0;
    }

    APS5_EXPORT("0BzLGljcwBo", unknown_0BzLGljcwBo_stub);
    int APS5_VABI unknown_0BzLGljcwBo_stub(void) {
        NotImplemented_nid_no_patch("unknown_0BzLGljcwBo_stub");
        return 0;
    }

    APS5_EXPORT("Z43vKp5k7r0", unknown_Z43vKp5k7r0_stub);
    int APS5_VABI unknown_Z43vKp5k7r0_stub(void) {
        NotImplemented_nid_no_patch("unknown_Z43vKp5k7r0_stub");
        return 0;
    }

    APS5_EXPORT("wED4ZXCFJT0", unknown_wED4ZXCFJT0_stub);
    int APS5_VABI unknown_wED4ZXCFJT0_stub(void) {
        NotImplemented_nid_no_patch("unknown_wED4ZXCFJT0_stub");
        return 0;
    }

    APS5_EXPORT("nF6bFRUBRAU", unknown_nF6bFRUBRAU_stub);
    int APS5_VABI unknown_nF6bFRUBRAU_stub(void) {
        NotImplemented_nid_no_patch("unknown_nF6bFRUBRAU_stub");
        return 0;
    }

    APS5_EXPORT("HlTPoZ-oY7Y", unknown_HlTPoZ_oY7Y_stub);
    int APS5_VABI unknown_HlTPoZ_oY7Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_HlTPoZ_oY7Y_stub");
        return 0;
    }

    APS5_EXPORT("GGsn7jMTxw4", unknown_GGsn7jMTxw4_stub);
    int APS5_VABI unknown_GGsn7jMTxw4_stub(void) {
        NotImplemented_nid_no_patch("unknown_GGsn7jMTxw4_stub");
        return 0;
    }

    APS5_EXPORT("ED9-Fjr8Ta4", unknown_ED9_Fjr8Ta4_stub);
    int APS5_VABI unknown_ED9_Fjr8Ta4_stub(void) {
        NotImplemented_nid_no_patch("unknown_ED9_Fjr8Ta4_stub");
        return 0;
    }

    APS5_EXPORT("thbPcG7E7qk", unknown_thbPcG7E7qk_stub);
    int APS5_VABI unknown_thbPcG7E7qk_stub(void) {
        NotImplemented_nid_no_patch("unknown_thbPcG7E7qk_stub");
        return 0;
    }

    APS5_EXPORT("jHdPvIzlpKc", unknown_jHdPvIzlpKc_stub);
    int APS5_VABI unknown_jHdPvIzlpKc_stub(void) {
        NotImplemented_nid_no_patch("unknown_jHdPvIzlpKc_stub");
        return 0;
    }

    APS5_EXPORT("oYM+YzfCm2Y", unknown_oYM_YzfCm2Y_stub);
    int APS5_VABI unknown_oYM_YzfCm2Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_oYM_YzfCm2Y_stub");
        return 0;
    }

    APS5_EXPORT("4v+otIIdjqg", unknown_4v_otIIdjqg_stub);
    int APS5_VABI unknown_4v_otIIdjqg_stub(void) {
        NotImplemented_nid_no_patch("unknown_4v_otIIdjqg_stub");
        return 0;
    }

    APS5_EXPORT("cUCo8OvArrw", unknown_cUCo8OvArrw_stub);
    int APS5_VABI unknown_cUCo8OvArrw_stub(void) {
        NotImplemented_nid_no_patch("unknown_cUCo8OvArrw_stub");
        return 0;
    }

    APS5_EXPORT("yb2cRhagD1I", unknown_yb2cRhagD1I_stub);
    int APS5_VABI unknown_yb2cRhagD1I_stub(void) {
        NotImplemented_nid_no_patch("unknown_yb2cRhagD1I_stub");
        return 0;
    }

    APS5_EXPORT("im2ZuItabu4", unknown_im2ZuItabu4_stub);
    int APS5_VABI unknown_im2ZuItabu4_stub(void) {
        NotImplemented_nid_no_patch("unknown_im2ZuItabu4_stub");
        return 0;
    }

    APS5_EXPORT("stDSYW2SBVM", unknown_stDSYW2SBVM_stub);
    int APS5_VABI unknown_stDSYW2SBVM_stub(void) {
        NotImplemented_nid_no_patch("unknown_stDSYW2SBVM_stub");
        return 0;
    }

    APS5_EXPORT("TLV4mswiZ4A", unknown_TLV4mswiZ4A_stub);
    int APS5_VABI unknown_TLV4mswiZ4A_stub(void) {
        NotImplemented_nid_no_patch("unknown_TLV4mswiZ4A_stub");
        return 0;
    }

    APS5_EXPORT("yhFCnaz5daw", unknown_yhFCnaz5daw_stub);
    int APS5_VABI unknown_yhFCnaz5daw_stub(void) {
        NotImplemented_nid_no_patch("unknown_yhFCnaz5daw_stub");
        return 0;
    }

    APS5_EXPORT("fhKwCVVj9nk", unknown_fhKwCVVj9nk_stub);
    int APS5_VABI unknown_fhKwCVVj9nk_stub(void) {
        NotImplemented_nid_no_patch("unknown_fhKwCVVj9nk_stub");
        return 0;
    }

    APS5_EXPORT("k8EXkhIP+lM", unknown_k8EXkhIP_lM_stub);
    int APS5_VABI unknown_k8EXkhIP_lM_stub(void) {
        NotImplemented_nid_no_patch("unknown_k8EXkhIP_lM_stub");
        return 0;
    }

    APS5_EXPORT("nLM2i2+65hA", unknown_nLM2i2_65hA_stub);
    int APS5_VABI unknown_nLM2i2_65hA_stub(void) {
        NotImplemented_nid_no_patch("unknown_nLM2i2_65hA_stub");
        return 0;
    }

    APS5_EXPORT("GNlx+y7xPdE", unknown_GNlx_y7xPdE_stub);
    int APS5_VABI unknown_GNlx_y7xPdE_stub(void) {
        NotImplemented_nid_no_patch("unknown_GNlx_y7xPdE_stub");
        return 0;
    }

    APS5_EXPORT("mLVL7N7BVBg", unknown_mLVL7N7BVBg_stub);
    int APS5_VABI unknown_mLVL7N7BVBg_stub(void) {
        NotImplemented_nid_no_patch("unknown_mLVL7N7BVBg_stub");
        return 0;
    }

    APS5_EXPORT("V31V01UiScY", unknown_V31V01UiScY_stub);
    int APS5_VABI unknown_V31V01UiScY_stub(void) {
        NotImplemented_nid_no_patch("unknown_V31V01UiScY_stub");
        return 0;
    }

    APS5_EXPORT("R6z1xM3pW-w", unknown_R6z1xM3pW_w_stub);
    int APS5_VABI unknown_R6z1xM3pW_w_stub(void) {
        NotImplemented_nid_no_patch("unknown_R6z1xM3pW_w_stub");
        return 0;
    }

    APS5_EXPORT("d88anrgNoKY", unknown_d88anrgNoKY_stub);
    int APS5_VABI unknown_d88anrgNoKY_stub(void) {
        NotImplemented_nid_no_patch("unknown_d88anrgNoKY_stub");
        return 0;
    }

    APS5_EXPORT("Fa3x75OOLRA", unknown_Fa3x75OOLRA_stub);
    int APS5_VABI unknown_Fa3x75OOLRA_stub(void) {
        NotImplemented_nid_no_patch("unknown_Fa3x75OOLRA_stub");
        return 0;
    }

    APS5_EXPORT("4Mv9OXypBG8", unknown_4Mv9OXypBG8_stub);
    int APS5_VABI unknown_4Mv9OXypBG8_stub(void) {
        NotImplemented_nid_no_patch("unknown_4Mv9OXypBG8_stub");
        return 0;
    }

    APS5_EXPORT("iBt3Oe00Kvc", unknown_iBt3Oe00Kvc_stub);
    int APS5_VABI unknown_iBt3Oe00Kvc_stub(void) {
        NotImplemented_nid_no_patch("unknown_iBt3Oe00Kvc_stub");
        return 0;
    }

    APS5_EXPORT("SXw4dZEkgpA", unknown_SXw4dZEkgpA_stub);
    int APS5_VABI unknown_SXw4dZEkgpA_stub(void) {
        NotImplemented_nid_no_patch("unknown_SXw4dZEkgpA_stub");
        return 0;
    }

    APS5_EXPORT("BgM3t3LvcNk", unknown_BgM3t3LvcNk_stub);
    int APS5_VABI unknown_BgM3t3LvcNk_stub(void) {
        NotImplemented_nid_no_patch("unknown_BgM3t3LvcNk_stub");
        return 0;
    }

    APS5_EXPORT("qGP74T5OWJc", unknown_qGP74T5OWJc_stub);
    int APS5_VABI unknown_qGP74T5OWJc_stub(void) {
        NotImplemented_nid_no_patch("unknown_qGP74T5OWJc_stub");
        return 0;
    }

    APS5_EXPORT("hsZPf1lON7E", unknown_hsZPf1lON7E_stub);
    int APS5_VABI unknown_hsZPf1lON7E_stub(void) {
        NotImplemented_nid_no_patch("unknown_hsZPf1lON7E_stub");
        return 0;
    }

    APS5_EXPORT("RX7XCNSaL6I", unknown_RX7XCNSaL6I_stub);
    int APS5_VABI unknown_RX7XCNSaL6I_stub(void) {
        NotImplemented_nid_no_patch("unknown_RX7XCNSaL6I_stub");
        return 0;
    }

    APS5_EXPORT("UoYY0DWMC0U", unknown_UoYY0DWMC0U_stub);
    int APS5_VABI unknown_UoYY0DWMC0U_stub(void) {
        NotImplemented_nid_no_patch("unknown_UoYY0DWMC0U_stub");
        return 0;
    }

    APS5_EXPORT("H7-fgvEutM0", unknown_H7_fgvEutM0_stub);
    int APS5_VABI unknown_H7_fgvEutM0_stub(void) {
        NotImplemented_nid_no_patch("unknown_H7_fgvEutM0_stub");
        return 0;
    }

    APS5_EXPORT("oL4hGI1PMpw", unknown_oL4hGI1PMpw_stub);
    int APS5_VABI unknown_oL4hGI1PMpw_stub(void) {
        NotImplemented_nid_no_patch("unknown_oL4hGI1PMpw_stub");
        return 0;
    }

    APS5_EXPORT("Fwvh++m9IQI", unknown_Fwvh__m9IQI_stub);
    int APS5_VABI unknown_Fwvh__m9IQI_stub(void) {
        NotImplemented_nid_no_patch("unknown_Fwvh__m9IQI_stub");
        return 0;
    }

    APS5_EXPORT("tZCSL5ulnB4", unknown_tZCSL5ulnB4_stub);
    int APS5_VABI unknown_tZCSL5ulnB4_stub(void) {
        NotImplemented_nid_no_patch("unknown_tZCSL5ulnB4_stub");
        return 0;
    }

    APS5_EXPORT("iFirFzgYsvw", unknown_iFirFzgYsvw_stub);
    int APS5_VABI unknown_iFirFzgYsvw_stub(void) {
        NotImplemented_nid_no_patch("unknown_iFirFzgYsvw_stub");
        return 0;
    }

    APS5_EXPORT("KnldROUkWJY", unknown_KnldROUkWJY_stub);
    int APS5_VABI unknown_KnldROUkWJY_stub(void) {
        NotImplemented_nid_no_patch("unknown_KnldROUkWJY_stub");
        return 0;
    }

    APS5_EXPORT("FFVZcCu3zWU", unknown_FFVZcCu3zWU_stub);
    int APS5_VABI unknown_FFVZcCu3zWU_stub(void) {
        NotImplemented_nid_no_patch("unknown_FFVZcCu3zWU_stub");
        return 0;
    }

    APS5_EXPORT("QJjPjlmPAL0", unknown_QJjPjlmPAL0_stub);
    int APS5_VABI unknown_QJjPjlmPAL0_stub(void) {
        NotImplemented_nid_no_patch("unknown_QJjPjlmPAL0_stub");
        return 0;
    }

    APS5_EXPORT("dewXw5roLs0", unknown_dewXw5roLs0_stub);
    int APS5_VABI unknown_dewXw5roLs0_stub(void) {
        NotImplemented_nid_no_patch("unknown_dewXw5roLs0_stub");
        return 0;
    }

    APS5_EXPORT("fzJdEihTFV4", unknown_fzJdEihTFV4_stub);
    int APS5_VABI unknown_fzJdEihTFV4_stub(void) {
        NotImplemented_nid_no_patch("unknown_fzJdEihTFV4_stub");
        return 0;
    }

    APS5_EXPORT("4PKnYXOhcx4", unknown_4PKnYXOhcx4_stub);
    int APS5_VABI unknown_4PKnYXOhcx4_stub(void) {
        NotImplemented_nid_no_patch("unknown_4PKnYXOhcx4_stub");
        return 0;
    }

    APS5_EXPORT("O0S96YnD04U", unknown_O0S96YnD04U_stub);
    int APS5_VABI unknown_O0S96YnD04U_stub(void) {
        NotImplemented_nid_no_patch("unknown_O0S96YnD04U_stub");
        return 0;
    }

    APS5_EXPORT("UBv7FkVfzcQ", unknown_UBv7FkVfzcQ_stub);
    int APS5_VABI unknown_UBv7FkVfzcQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_UBv7FkVfzcQ_stub");
        return 0;
    }

    APS5_EXPORT("bdqdvIkLPIU", unknown_bdqdvIkLPIU_stub);
    int APS5_VABI unknown_bdqdvIkLPIU_stub(void) {
        NotImplemented_nid_no_patch("unknown_bdqdvIkLPIU_stub");
        return 0;
    }

    APS5_EXPORT("UoBuWAhKk7U", unknown_UoBuWAhKk7U_stub);
    int APS5_VABI unknown_UoBuWAhKk7U_stub(void) {
        NotImplemented_nid_no_patch("unknown_UoBuWAhKk7U_stub");
        return 0;
    }

    APS5_EXPORT("nEyFbYUloIM", unknown_nEyFbYUloIM_stub);
    int APS5_VABI unknown_nEyFbYUloIM_stub(void) {
        NotImplemented_nid_no_patch("unknown_nEyFbYUloIM_stub");
        return 0;
    }

    APS5_EXPORT("k7iGTvDQPLQ", unknown_k7iGTvDQPLQ_stub);
    int APS5_VABI unknown_k7iGTvDQPLQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_k7iGTvDQPLQ_stub");
        return 0;
    }

    APS5_EXPORT("ln33zjBrfjk", unknown_ln33zjBrfjk_stub);
    int APS5_VABI unknown_ln33zjBrfjk_stub(void) {
        NotImplemented_nid_no_patch("unknown_ln33zjBrfjk_stub");
        return 0;
    }

    APS5_EXPORT("5SHGNwLXBV4", unknown_5SHGNwLXBV4_stub);
    int APS5_VABI unknown_5SHGNwLXBV4_stub(void) {
        NotImplemented_nid_no_patch("unknown_5SHGNwLXBV4_stub");
        return 0;
    }

    APS5_EXPORT("HzMN7ANqYEc", unknown_HzMN7ANqYEc_stub);
    int APS5_VABI unknown_HzMN7ANqYEc_stub(void) {
        NotImplemented_nid_no_patch("unknown_HzMN7ANqYEc_stub");
        return 0;
    }

    APS5_EXPORT("rTIV11nMQuM", unknown_rTIV11nMQuM_stub);
    int APS5_VABI unknown_rTIV11nMQuM_stub(void) {
        NotImplemented_nid_no_patch("unknown_rTIV11nMQuM_stub");
        return 0;
    }

    APS5_EXPORT("NfvOrNzy6sk", unknown_NfvOrNzy6sk_stub);
    int APS5_VABI unknown_NfvOrNzy6sk_stub(void) {
        NotImplemented_nid_no_patch("unknown_NfvOrNzy6sk_stub");
        return 0;
    }

    APS5_EXPORT("7qZVNgEu+SY", unknown_7qZVNgEu_SY_stub);
    int APS5_VABI unknown_7qZVNgEu_SY_stub(void) {
        NotImplemented_nid_no_patch("unknown_7qZVNgEu_SY_stub");
        return 0;
    }

    APS5_EXPORT("aPIZJTXC+cU", unknown_aPIZJTXC_cU_stub);
    int APS5_VABI unknown_aPIZJTXC_cU_stub(void) {
        NotImplemented_nid_no_patch("unknown_aPIZJTXC_cU_stub");
        return 0;
    }

    APS5_EXPORT("W1Etj-jlW7Y", unknown_W1Etj_jlW7Y_stub);
    int APS5_VABI unknown_W1Etj_jlW7Y_stub(void) {
        NotImplemented_nid_no_patch("unknown_W1Etj_jlW7Y_stub");
        return 0;
    }

    APS5_EXPORT("aj3L-iaFmyk", unknown_aj3L_iaFmyk_stub);
    int APS5_VABI unknown_aj3L_iaFmyk_stub(void) {
        NotImplemented_nid_no_patch("unknown_aj3L_iaFmyk_stub");
        return 0;
    }

    APS5_EXPORT("jiItzS6+22g", unknown_jiItzS6_22g_stub);
    int APS5_VABI unknown_jiItzS6_22g_stub(void) {
        NotImplemented_nid_no_patch("unknown_jiItzS6_22g_stub");
        return 0;
    }

    APS5_EXPORT("1qXLHIpROPE", unknown_1qXLHIpROPE_stub);
    int APS5_VABI unknown_1qXLHIpROPE_stub(void) {
        NotImplemented_nid_no_patch("unknown_1qXLHIpROPE_stub");
        return 0;
    }

    APS5_EXPORT("MBMa6EFu4Ko", unknown_MBMa6EFu4Ko_stub);
    int APS5_VABI unknown_MBMa6EFu4Ko_stub(void) {
        NotImplemented_nid_no_patch("unknown_MBMa6EFu4Ko_stub");
        return 0;
    }

    APS5_EXPORT("jg33rEKLfVs", unknown_jg33rEKLfVs_stub);
    int APS5_VABI unknown_jg33rEKLfVs_stub(void) {
        NotImplemented_nid_no_patch("unknown_jg33rEKLfVs_stub");
        return 0;
    }

    APS5_EXPORT("26PM5Mzl8zc", unknown_26PM5Mzl8zc_stub);
    int APS5_VABI unknown_26PM5Mzl8zc_stub(void) {
        NotImplemented_nid_no_patch("unknown_26PM5Mzl8zc_stub");
        return 0;
    }

    APS5_EXPORT("RU74kek-N0c", unknown_RU74kek_N0c_stub);
    int APS5_VABI unknown_RU74kek_N0c_stub(void) {
        NotImplemented_nid_no_patch("unknown_RU74kek_N0c_stub");
        return 0;
    }

    APS5_EXPORT("Kl0Z3LH07QI", unknown_Kl0Z3LH07QI_stub);
    int APS5_VABI unknown_Kl0Z3LH07QI_stub(void) {
        NotImplemented_nid_no_patch("unknown_Kl0Z3LH07QI_stub");
        return 0;
    }

    APS5_EXPORT("29oKvKXzEZo", unknown_29oKvKXzEZo_stub);
    int APS5_VABI unknown_29oKvKXzEZo_stub(void) {
        NotImplemented_nid_no_patch("unknown_29oKvKXzEZo_stub");
        return 0;
    }

    APS5_EXPORT("A+uGq+3KFtQ", unknown_A_uGq_3KFtQ_stub);
    int APS5_VABI unknown_A_uGq_3KFtQ_stub(void) {
        NotImplemented_nid_no_patch("unknown_A_uGq_3KFtQ_stub");
        return 0;
    }

    APS5_EXPORT("Q7t4VEYLafI", unknown_Q7t4VEYLafI_stub);
    int APS5_VABI unknown_Q7t4VEYLafI_stub(void) {
        NotImplemented_nid_no_patch("unknown_Q7t4VEYLafI_stub");
        return 0;
    }

    APS5_EXPORT("u9YKpRRHe-M", unknown_u9YKpRRHe_M_stub);
    int APS5_VABI unknown_u9YKpRRHe_M_stub(void) {
        NotImplemented_nid_no_patch("unknown_u9YKpRRHe_M_stub");
        return 0;
    }

    APS5_EXPORT("f33OrruQYbM", unknown_f33OrruQYbM_stub);
    int APS5_VABI unknown_f33OrruQYbM_stub(void) {
        NotImplemented_nid_no_patch("unknown_f33OrruQYbM_stub");
        return 0;
    }

    APS5_EXPORT("6IMbpR7nTzA", unknown_6IMbpR7nTzA_stub);
    int APS5_VABI unknown_6IMbpR7nTzA_stub(void) {
        NotImplemented_nid_no_patch("unknown_6IMbpR7nTzA_stub");
        return 0;
    }

    APS5_EXPORT("9Mv61HaMhfA", unknown_9Mv61HaMhfA_stub);
    int APS5_VABI unknown_9Mv61HaMhfA_stub(void) {
        NotImplemented_nid_no_patch("unknown_9Mv61HaMhfA_stub");
        return 0;
    }

    APS5_EXPORT("ZFqKFl23aMc", unknown_ZFqKFl23aMc_stub);
    int APS5_VABI unknown_ZFqKFl23aMc_stub(void) {
        NotImplemented_nid_no_patch("unknown_ZFqKFl23aMc_stub");
        return 0;
    }

    APS5_EXPORT("nvEwfYAImTs", unknown_nvEwfYAImTs_stub);
    int APS5_VABI unknown_nvEwfYAImTs_stub(void) {
        NotImplemented_nid_no_patch("unknown_nvEwfYAImTs_stub");
        return 0;
    }

    APS5_EXPORT("gObODli-OH8", unknown_gObODli_OH8_stub);
    int APS5_VABI unknown_gObODli_OH8_stub(void) {
        NotImplemented_nid_no_patch("unknown_gObODli_OH8_stub");
        return 0;
    }

    APS5_EXPORT("6YRHhh5mHCs", unknown_6YRHhh5mHCs_stub);
    int APS5_VABI unknown_6YRHhh5mHCs_stub(void) {
        NotImplemented_nid_no_patch("unknown_6YRHhh5mHCs_stub");
        return 0;
    }

    APS5_EXPORT("f85orjx7qts", unknown_f85orjx7qts_stub);
    int APS5_VABI unknown_f85orjx7qts_stub(void) {
        NotImplemented_nid_no_patch("unknown_f85orjx7qts_stub");
        return 0;
    }

    APS5_EXPORT("MYRtYhojKdA", unknown_MYRtYhojKdA_stub);
    int APS5_VABI unknown_MYRtYhojKdA_stub(void) {
        NotImplemented_nid_no_patch("unknown_MYRtYhojKdA_stub");
        return 0;
    }

    APS5_EXPORT("dGYo9mE8K2A", unknown_dGYo9mE8K2A_stub);
    int APS5_VABI unknown_dGYo9mE8K2A_stub(void) {
        NotImplemented_nid_no_patch("unknown_dGYo9mE8K2A_stub");
        return 0;
    }

    APS5_EXPORT("xZqiZvmcp9k", unknown_xZqiZvmcp9k_stub);
    int APS5_VABI unknown_xZqiZvmcp9k_stub(void) {
        NotImplemented_nid_no_patch("unknown_xZqiZvmcp9k_stub");
        return 0;
    }

    APS5_EXPORT("W0j6vCxh9Pc", unknown_W0j6vCxh9Pc_stub);
    int APS5_VABI unknown_W0j6vCxh9Pc_stub(void) {
        NotImplemented_nid_no_patch("unknown_W0j6vCxh9Pc_stub");
        return 0;
    }

}
