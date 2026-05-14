# C to Python Converter

A lightweight source-to-source converter that translates a subset of **C programs** into equivalent **Python code** using parsing and syntax transformation techniques.

---

# 📌 Project Overview

This project converts basic C syntax into readable Python code by applying rule-based transformations.

It is designed to help beginners understand the relationship between C and Python syntax while also demonstrating concepts of parsing, tokenization, and code translation.

The converter reads a `.c` file as input and generates a corresponding `.py` file as output.

---

# ✨ Supported Features

## ✅ Variable Declarations

Supports:

- `int`
- `float`
- `double`
- `char`
- `bool`

### Example

### C

```c
int a;
float x = 5.5;
int p = 1, q = 2;
```

### Python

```python
a = 0
x = 5.5
p, q = 1, 2
```

---

## ✅ Conditional Statements

### Supported

- `if`
- `else if`
- `else`

### Example

### C

```c
if (a > b) {
    printf("A");
}
else if (a == b) {
    printf("Equal");
}
else {
    printf("B");
}
```

### Python

```python
if a > b:
    print("A")

elif a == b:
    print("Equal")

else:
    print("B")
```

---

## ✅ Loop Conversion

### While Loop

### C

```c
while (i < 5) {
    i++;
}
```

### Python

```python
while i < 5:
    i += 1
```

---

### For Loop → While Loop

`for` loops are internally converted into Python `while` loops.

### C

```c
for (i = 0; i < 10; i++) {
    printf("%d", i);
}
```

### Python

```python
i = 0

while i < 10:
    print(i)
    i += 1
```

---

### Do-While Loop

### C

```c
do {
    i++;
} while (i < 5);
```

### Python

```python
while True:
    i += 1

    if not (i < 5):
        break
```

---

## ✅ Increment / Decrement Operators

### C

```c
i++;
j--;
```

### Python

```python
i += 1
j -= 1
```

---

## ✅ Functions

Supports user-defined functions with parameters.

### C

```c
int add(int a, int b) {
    return a + b;
}
```

### Python

```python
def add(a, b):
    return a + b
```

---

## ✅ Input Handling (`scanf`)

### Supported Specifiers

| C Specifier | Python Conversion |
|---|---|
| `%d` | `int(input())` |
| `%f` | `float(input())` |

### Example

### C

```c
scanf("%d", &a);
scanf("%f", &x);
```

### Python

```python
a = int(input())
x = float(input())
```

### Multiple Inputs

If multiple variables are present in a single `scanf`, the converter generates separate input statements.

### C

```c
scanf("%d %d", &a, &b);
```

### Python

```python
a = int(input())
b = int(input())
```

---

## ✅ Output Handling (`printf`)

### C

```c
printf("Value = %d", a);
```

### Python

```python
print("Value = {}".format(a))
```

### Float Example

### C

```c
printf("%f", x);
```

### Python

```python
print("{}".format(x))
```

---

# 🔄 Additional Transformations

## ✅ `#include` Handling

C header files are ignored during conversion.

### C

```c
#include <stdio.h>
```

### Python

```python
# Ignored
```

---

## ✅ `#define` Handling

Macro constants are replaced with equivalent Python assignments.

### C

```c
#define MAX 100
```

### Python

```python
MAX = 100
```

---

## ✅ Comment Conversion

### Single-Line Comments

### C

```c
// This is a comment
```

### Python

```python
# This is a comment
```

---

### Multi-Line Comments

### C

```c
/* Multi-line
   comment */
```

### Python

```python
'''
Multi-line
comment
'''
```

---

## ✅ Integer Division Handling

If both numerator and denominator are integers, `/` is converted to `//`.

### C

```c
a = b / c;
```

### Python

```python
a = b // c
```

---

## ✅ Block End Markers

Whenever a `}` is encountered, the converter adds a Python comment to indicate block termination.

### Example

```python
# End of block
```

---

# 🧮 Matrix Operations (Experimental)

The project also attempts basic conversion for:

- Matrix Addition
- Matrix Multiplication

This feature is currently experimental and under improvement.

---

# ⚙️ Assumptions

- Input C code is assumed to be **syntactically correct**
- No semantic error checking is performed
- Only a subset of C syntax is supported

---

# 📂 Input / Output

## Input

- `.c` source file

## Output

- Generated `.py` file

---

# 🚀 Future Improvements

- Support for arrays and pointers
- Better expression parsing
- Switch-case conversion
- Struct and class support
- Nested function handling
- Advanced matrix operations
- Error detection and reporting
- GUI interface for file conversion

---

# 🛠️ Technologies Used

- Python
- Regular Expressions
- File Handling
- Parsing Logic
- String Manipulation

---

# 🎯 Learning Outcomes

This project demonstrates:

- Compiler design basics
- Syntax transformation
- Parsing techniques
- Language translation concepts
- Rule-based code conversion

---

# 📌 Conclusion

The **C to Python Converter** successfully translates fundamental C constructs into Python syntax while maintaining readability and logical structure.

It serves as both an educational tool and a foundation for more advanced source-code translation systems.