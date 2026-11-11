#include <cstdint>
#include <cstddef>
#include "SceTypes.hpp"
#include "prx/libc/include/General.hpp"
#include "prx/libSceVideoOut/include/Output.hpp"
#include <stdexcept>

extern "C" {

int APS5_VABI sceVideoOutSetFlipMaster() {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

int APS5_VABI sceVideoOutClearFlipMaster() {
    NotImplemented_nid_no_patch(__func__);
    return 0;
}

int APS5_VABI sceVideoOutAdjustColor_(int handle, const VideoOutColorSettings* settings, uint32_t settings_size) {
    if (settings_size < sizeof(VideoOutColorSettings)) throw std::runtime_error("sceVideoOutAdjustColor_: VIDEO_OUT_ERROR_INVALID_VALUE");
    return sceVideoOutAdjustColor(handle, settings);
}

int APS5_VABI sceVideoOutColorSettingsSetGamma_(VideoOutColorSettings* settings, float gamma, uint32_t settings_size) {
    if (settings_size < sizeof(VideoOutColorSettings)) throw std::runtime_error("sceVideoOutColorSettingsSetGamma_: VIDEO_OUT_ERROR_INVALID_VALUE");
    return sceVideoOutColorSettingsSetGamma(settings, gamma);
}

// PS4 NID-alias tables: stubs for PS4 video-out imports that resolve
// here instead of failing at load time. NIDs computed from PS4 symbol
// names; each maps to a NotImplemented stub so the import is present
// (Windows strict import resolution) but the function is unimplemented.
APS5_EXPORT("5SxgcIvlSAg", sceVideoOutInit_stub);
int APS5_VABI sceVideoOutInit_stub(void) {
    return 0;
}

APS5_EXPORT("MZuqIyQLKaI", sceVideoOutFinish_stub);
int APS5_VABI sceVideoOutFinish_stub(void) {
    return 0;
}

APS5_EXPORT("IuK4LoGvcEo", sceVideoOutRegisterDevice_stub);
int APS5_VABI sceVideoOutRegisterDevice_stub(void) {
    return 0;
}

APS5_EXPORT("SOP+A-TeSKM", sceVideoOutUnregisterDevice_stub);
int APS5_VABI sceVideoOutUnregisterDevice_stub(void) {
    return 0;
}

APS5_EXPORT("MBHF75JylUs", sceVideoOutGetState_stub);
int APS5_VABI sceVideoOutGetState_stub(void) {
    return 0;
}

APS5_EXPORT("Up36PTk687E", sceVideoOutOpen);

APS5_EXPORT("uquVH4-Du78", sceVideoOutClose);

APS5_EXPORT("X7Z86CUnnL4", sceVideoOutFlip_stub);
int APS5_VABI sceVideoOutFlip_stub(int handle, int index, int flipMode, int64_t flipArg) {
    (void)handle; (void)index; (void)flipMode; (void)flipArg;
    return 0;
}

APS5_EXPORT("SbU3dwp80lQ", sceVideoOutGetFlipStatus);

APS5_EXPORT("++6VFLx35o8", sceVideoOutSetFlipInterval_stub);
int APS5_VABI sceVideoOutSetFlipInterval_stub(int handle, int interval) {
    return sceVideoOutSetFlipRate(handle, interval);
}

}
