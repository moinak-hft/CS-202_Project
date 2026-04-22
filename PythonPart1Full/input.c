#include <stdio.h>
int main()
{
    int x = 2 + 3;
    int y = x + 5;
    int z = y + x;
    //trying comment removal
    if (1 + 2 > 2)
    {
        int a = z + 5;
        x = a + 10;
    }
    else
    {
        int dead1 = 100;
        x = 200;
    }

    int b = x + 5;

    while (0)
    {
        int dead2 = 999;
        b = 0;
    }

    if (0)
    {
        int dead3 = 50;
    }
    else
    {
        int c = b + 5;
        return c;
        int dead4 = 777;
    }

    int dead5 = 123;

    printf("%d", z);

    return 0;
}