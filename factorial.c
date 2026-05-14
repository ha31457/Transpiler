#include <stdio.h>

// Function to calculate factorial
int factorial(int n) {
    int i, fact = 1;

    for(i = 1; i <= n; i++) {
        fact = fact * i;
    }

    return fact;
}

int main() {
    int num;

    printf("Enter a number: ");
    scanf("%d", &num);

    if(num < 0) {
        printf("Negative number not allowed\n");
    }
    else if(num == 0) {
        printf("Factorial is 1\n");
    }
    else {
        int result = factorial(num);
        printf("Factorial of %d is %d\n", num, result);
    }

    // while loop test
    int i = 0;
    while(i < 3) {
        printf("i = %d\n", i);
        i++;
    }

    return 0;
}