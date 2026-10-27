#include <windows.h>
__declspec(dllexport) void TestExport() {}
BOOL WINAPI DllMain(HINSTANCE h, DWORD r, LPVOID p) { return TRUE; }