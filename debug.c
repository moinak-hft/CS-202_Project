#include<stdio.h>

int main()
{
    int l = 2;
    
    int a = 5;
    int b = 10;

    int x = 2 + 3 * 4;     // Constant Folding

    int y = a + b;   
    printf("%d", &y);      // Constant Propagation
   
    if (1)
    {
        int dead777 = y + 1;
        foo();
        return dead777;
        
        
    }

    while (0)
    {
        int dead888 = b + 1;
        return b;
        b = dead888;
    }

    int unused999 = 100;   // UAE

    return unused999;
    int unused9994 = 100;

}