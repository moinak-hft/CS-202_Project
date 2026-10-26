#include <stdio.h>
#include <stdlib.h>

#ifndef N
#define N 16384
#endif

/* Experiment: allow inlining; function body is unchanged. */
static unsigned int step(unsigned int value)
{
    return (value * 3u) ^ 0x9e3779b9u;
}

int main(int argc, char **argv)
{
    unsigned int data[N];
    unsigned int rounds = argc > 1 ? (unsigned int)strtoul(argv[1], 0, 10) : 400u;
    unsigned int checksum = 0u;
    if (rounds > 10000u) return 2;
    for (unsigned int i = 0; i < N; ++i) data[i] = i + 17u;
    for (unsigned int r = 0; r < rounds; ++r) {
        for (unsigned int i = 0; i < N; ++i) {
            data[i] = step(data[i]);
        }
    }
    for (unsigned int i = 0; i < N; ++i) checksum ^= data[i];
    printf("%u\n", checksum);
    return 0;
}
