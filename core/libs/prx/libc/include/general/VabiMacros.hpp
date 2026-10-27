#ifndef CORE_LIBS_PRX_LIBC_INCLUDE_GENERAL_GENERALMACROS_HPP
#define CORE_LIBS_PRX_LIBC_INCLUDE_GENERAL_GENERALMACROS_HPP

#if defined(__clang__) || defined(__GNUC__)
#ifdef _WIN32
#define APS5_VABI __attribute__((sysv_abi))
#endif
#endif
#ifndef APS5_VABI
#define APS5_VABI
#endif

#endif
