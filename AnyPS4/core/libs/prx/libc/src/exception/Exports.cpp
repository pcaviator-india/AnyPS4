#if defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#endif

#include "Unwind.cpp"
#include "Runtime.cpp"
#include "TypeInfo.cpp"
#include "ExceptionPointer.cpp"
#include "StandardExceptions.cpp"
#include "ArraySupport.cpp"
#include "GuardSupport.cpp"
#include "Personality.cpp"

#include "prx/libc/include/General.hpp"

#if defined(__clang__) || defined(__GNUC__)
#include "prx/libc/include/specifics/gcc/SymbolAlias.hpp"
#endif

extern "C" [[noreturn]] void APS5_VABI LibcRuntimeAssertion(const char*, int, const char*, const char*) { std::abort(); }

#if defined(__clang__) || defined(__GNUC__)
GCC_LOCAL_ALIAS(_ZSt21__glibcxx_assert_failPKciS0_S0_, LibcRuntimeAssertion);
GCC_GLOBAL_ALIAS(__cxa_allocate_exception_nid_no_patch_cut, __cxa_allocate_exception_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_throw_nid_no_patch_cut, __cxa_throw_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_begin_catch_nid_no_patch_cut, __cxa_begin_catch_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_end_catch_nid_no_patch_cut, __cxa_end_catch_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_rethrow_nid_no_patch_cut, __cxa_rethrow_nid_postfix);
GCC_GLOBAL_ALIAS(__gxx_personality_v0_nid_no_patch_cut, __gxx_personality_v0_nid_postfix);
GCC_GLOBAL_ALIAS(_Unwind_Resume_nid_no_patch_cut, _Unwind_Resume_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_free_exception, __cxa_free_exception_nid_postfix);
GCC_GLOBAL_ALIAS(_ZSt9terminatev, _ZSt9terminatev_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_call_terminate, __cxa_call_terminate_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_allocate_exception, __cxa_allocate_exception_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_throw, __cxa_throw_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_init_primary_exception, __cxa_init_primary_exception_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_begin_catch, __cxa_begin_catch_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_end_catch, __cxa_end_catch_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_rethrow, __cxa_rethrow_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_get_exception_ptr, __cxa_get_exception_ptr_nid_postfix);
GCC_GLOBAL_ALIAS(__cxa_current_exception_type, __cxa_current_exception_type_nid_postfix);
GCC_GLOBAL_ALIAS(_ZSt13set_terminatePFvvE, _ZSt13set_terminatePFvvE_nid_postfix);
GCC_GLOBAL_ALIAS(_ZSt13get_terminatev, _ZSt13get_terminatev_nid_postfix);
GCC_GLOBAL_ALIAS(_ZSt18uncaught_exceptionv, _ZSt18uncaught_exceptionv_nid_postfix);
GCC_GLOBAL_ALIAS(_ZSt19uncaught_exceptionsv, _ZSt19uncaught_exceptionsv_nid_postfix);
GCC_GLOBAL_ALIAS(_Unwind_Resume, _Unwind_Resume_nid_postfix);
GCC_GLOBAL_ALIAS(_Unwind_RaiseException, _Unwind_RaiseException_nid_postfix);
GCC_GLOBAL_ALIAS(_Unwind_Resume_or_Rethrow, _Unwind_Resume_or_Rethrow_nid_postfix);
GCC_GLOBAL_ALIAS(_Unwind_DeleteException, _Unwind_DeleteException_nid_postfix);
#endif

#ifdef _WIN32
extern "C" {
void* NativeAllocateException(std::size_t size) {
    void* object = __cxa_allocate_exception_nid_postfix(size);
    LibcException::FromObject(object)->_pad = 1;
    return object;
}
void NativeFreeException(void* object) { __cxa_free_exception_nid_postfix(object); }
[[noreturn]] void NativeThrow(void* object, std::type_info* type, void (*destructor)(void*)) {
#if defined(_MSC_VER)
    ThrowFromSite(object, type, destructor, _ReturnAddress());
#else
    ThrowFromSite(object, type, destructor, __builtin_return_address(0));
#endif
}
void* NativeBeginCatch(void* exception) { return __cxa_begin_catch_nid_postfix(exception); }
void NativeEndCatch() { __cxa_end_catch_nid_postfix(); }
[[noreturn]] void NativeRethrow() { __cxa_rethrow_nid_postfix(); }
[[noreturn]] void NativeResume(_Unwind_Exception* exception) { _Unwind_Resume_nid_postfix(exception); }
[[noreturn]] void NativeTerminate() { LibcException::Terminate(); }
[[noreturn]] void NativeCallTerminate(void* exception) { __cxa_call_terminate_nid_postfix(exception); }
void* NativeExceptionPointer(void* exception) { return __cxa_get_exception_ptr_nid_postfix(exception); }
void* NativeGlobals() { return &LibcException::globals; }
void* NativeGlobalsFast() { return &LibcException::globals; }
unsigned NativeUncaughtExceptions() { return LibcException::globals.uncaught; }
bool NativeUncaughtException() { return LibcException::globals.uncaught != 0; }
bool NativeStdUncaughtException() { return LibcException::globals.uncaught != 0; }
int NativeStdUncaughtExceptions() { return static_cast<int>(LibcException::globals.uncaught); }
void* NativeInitPrimaryException(void* object, std::type_info* type, void (*destructor)(void*)) {
    return __cxa_init_primary_exception_nid_postfix(object, type, destructor);
}
}
#endif
