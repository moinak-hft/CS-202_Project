// Common C Header Files
#include <stdio.h>
#include <stdlib.h>
#include <string.h>        
// Macro definition: TRY expands to this statement
#define TRY int x = 2 + 3;  

int main()                  // Main function: program execution starts here
{
    TRY                     // Expands to: int x = 2 + 3;
    int y = x + 5;
    int z = y + x;

    // trying comment removal
    if (1 + 2 > 2)          // if condition: true, so this block executes
    {
        int a = z + 5;
        x = a + 10;
    }
    else                    // runs only if if-condition is false
    {
        int dead1 = 100;
        x = 200;
    }

    int b = x + 5;

    while (0)               // while condition is false, so this loop never runs
    {
        int dead2 = 999;
        b = 0;
    }

    if (0)                  // false condition, so this block never runs
    {
        int dead3 = 50;
    }
    else                    // this else block runs
    {
        int c = b + 5;
        return c;           // function ends here
        int dead4 = 777;    // unreachable code
    }

    int dead5 = 123;        // unreachable code after return

    printf("%d", z);        // prints z

    return 0;               // returns 0 from main
}
