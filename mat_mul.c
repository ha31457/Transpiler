#include <stdio.h>
#define N 3

/* Matrix Multiplication Program
   Multiplies two NxN matrices */

// Function to read a matrix from user input
void readMatrix(int mat[N][N], int rows, int cols) {
    int i, j;
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {
            // read each element
            scanf("%d", &mat[i][j]);
        }
    }
}

// Function to multiply two matrices
void multiplyMatrix(int a[N][N], int b[N][N], int result[N][N], int n) {
    int i, j, k;
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            result[i][j] = 0;
            for (k = 0; k < n; k++) {
                result[i][j] = result[i][j] + a[i][k] * b[k][j];
            }
        }
    }
}

// Function to print a matrix
void printMatrix(int mat[N][N], int rows, int cols) {
    int i, j;
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {
            printf("%d ", mat[i][j]);
        }
        printf("\n");
    }
}

int main() {
    int a[N][N], b[N][N], result[N][N];
    int rows = N, cols = N;

    /* Read first matrix */
    printf("Enter elements of first matrix:\n");
    readMatrix(a, rows, cols);

    // Read second matrix
    printf("Enter elements of second matrix:\n");
    readMatrix(b, rows, cols);

    multiplyMatrix(a, b, result, N);

    printf("Result of matrix multiplication:\n");
    printMatrix(result, rows, cols);

    return 0;
}