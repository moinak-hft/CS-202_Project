int choose(int flag)
{
    int x;
    if (flag) {
        x = 1;
    } else {
        x = 2;
    }
    return x;
}

int main(void)
{
    return choose(1);
}
