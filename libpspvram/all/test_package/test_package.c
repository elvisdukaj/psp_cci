#include <vram.h>
// #include <vramalloc.h>

int main(void) {
    void* b1;

    b1 = vramalloc(100);
    vfree(b1);
    
    return 0;
}
