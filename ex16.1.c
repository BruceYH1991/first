#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

struct Person {
    char *name;
    int age;
    int height;
    int weight;
};


void Person_print(struct Person who)
{
    printf("name: %s\n", who.name);
    printf("\tage: %d\n", who.age);
    printf("\theight: %d\n", who.height);
    printf("\tweight: %d\n", who.weight);
}

int main(int argc, char *argv[])
{
    struct Person joe = {"Joe Alex", 32, 64, 140};

    Person_print(joe);

    return 0;
}


















