#ifndef CORE_LIBS_PRX_SCE_TYPES_HPP
#define CORE_LIBS_PRX_SCE_TYPES_HPP

#include <cstdint>
#include <cstddef>

// Common PS4 type definitions used across PRX libraries

namespace sce {

// SceUID - handle type used by kernel and system libraries
using SceUID = int32_t;

// SceSize - size type
using SceSize = uint32_t;

// SceIntPtr / SceUIntPtr - pointer-sized integers
using SceIntPtr = intptr_t;
using SceUIntPtr = uintptr_t;

// SceBool - boolean type
using SceBool = int32_t;

} // namespace sce

#endif // CORE_LIBS_PRX_SCE_TYPES_HPP