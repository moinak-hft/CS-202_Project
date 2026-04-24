#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define BASE 10
#define OFFSET 5
#define DOUBLE(x) ((x) * 2)
#define ADD(x, y) ((x) + (y))
#define SHOULD_RUN 1
#define DEAD_LOOP 0

#ifdef SHOULD_RUN
#define FINAL_BONUS OFFSET
#else
#define FINAL_BONUS 100
#endif

int main()
{
    int seed = BASE;
    int scaled = DOUBLE(BASE + OFFSET);
    int total = ADD(scaled, seed);
    bool enabled = true;
    uint32_t unused_counter = 123;

    if (SHOULD_RUN)
    {
        int result = ADD(total, FINAL_BONUS);
        seed = result;
    }
    else
    {
        int never_used = 999;
        seed = never_used;
    }

    while (DEAD_LOOP)
    {
        total = ADD(total, 1);
        printf("%d", total);
    }

    if (seed > 40)
    {
        return seed;
    }
    else
    {
        printf("%d", total);
        return 0;
    }

    printf("unreachable");
    return 1;
}
