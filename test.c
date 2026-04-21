int f(int x) {
    int a = 0;
    if (x > 0) {
        a = 1;
    } else {
        a = 2;
    }

    while (a < 5) {
        a = a + 1;
    }

    return a;
}