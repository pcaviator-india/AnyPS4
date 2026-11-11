#include <windows.h>
#include <iostream>
#include <cstddef>

int main() {
    std::cout << "offsetof(CONTEXT, Rip) = " << offsetof(CONTEXT, Rip) << std::endl;
    std::cout << "offsetof(CONTEXT, Rax) = " << offsetof(CONTEXT, Rax) << std::endl;
    std::cout << "sizeof(CONTEXT) = " << sizeof(CONTEXT) << std::endl;
    return 0;
}