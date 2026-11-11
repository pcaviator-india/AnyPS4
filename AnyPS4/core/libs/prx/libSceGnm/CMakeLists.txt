add_library(libSceGnm SHARED EXCLUDE_FROM_ALL
    ${CMAKE_CURRENT_SOURCE_DIR}/Export.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/GnmState.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/GnmImpl.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/GnmVulkan.cpp
)
target_include_directories(libSceGnm PRIVATE
    ${LIBS_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${ANYPS5_VULKAN_HEADERS_INCLUDE_DIR}
    ${ANYPS5_SDL2_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/core/shader/recompiler
)
target_link_libraries(libSceGnm PRIVATE libSceVideoOut libSceAgcDriver libkernel libc SDL2-static shader_recompiler_agc_driver)
target_compile_definitions(libSceGnm PRIVATE VK_USE_PLATFORM_WIN32_KHR)
if(WIN32)
    target_link_libraries(libSceGnm PRIVATE C:/Windows/System32/vulkan-1.dll dxgi user32 gdi32)
endif()
set_target_properties(libSceGnm PROPERTIES CXX_EXTENSIONS OFF)
configure_windows_unwind(libSceGnm)