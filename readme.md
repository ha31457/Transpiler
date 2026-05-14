# ⚡ C to Python Transpiler

A modern source-to-source transpiler that converts a subset of **C programs** into clean and readable **Python code** using parsing, regex-based transformations, and syntax-aware conversion techniques.

The project also includes a fully interactive **Streamlit-based IDE-style web interface** with syntax highlighting, live editing, file uploads, downloads, conversion metrics, and a modern developer experience.

---

# 🚀 Project Overview

The **C to Python Transpiler** is designed to simplify the understanding of programming language translation by automatically converting C syntax into equivalent Python code.

The project demonstrates:

- Compiler design fundamentals
- Syntax parsing
- Lexical transformations
- Rule-based transpilation
- Source-to-source code conversion
- UI/UX integration with Streamlit

The application accepts a `.c` source file or raw C code as input and generates an equivalent `.py` file as output.

---

# ✨ Core Features

# ✅ Variable Declaration Conversion

Supports conversion of:

- `int`
- `float`
- `double`
- `char`
- `bool`
- `long`
- `short`

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

# ✅ Conditional Statement Conversion

Supports:

- `if`
- `else if`
- `else`

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

# ✅ Loop Conversion

## While Loop

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

## For Loop → While Loop

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

## Do-While Loop

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

# ✅ Function Conversion

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

# ✅ Increment & Decrement Operators

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

# ✅ Input Handling (`scanf`)

Supports automatic Python input conversion.

| C Specifier | Python Conversion |
|---|---|
| `%d` | `int(input())` |
| `%f` | `float(input())` |
| `%s` | `input()` |

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

---

## Multiple Inputs

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

# ✅ Output Handling (`printf`)

### C

```c
printf("Value = %d", a);
```

### Python

```python
print("Value = {}".format(a))
```

---

# 🔄 Additional Transformations

# ✅ `#define` Handling

### C

```c
#define MAX 100
```

### Python

```python
MAX = 100
```

---

# ✅ Comment Conversion

## Single-Line Comments

### C

```c
// This is a comment
```

### Python

```python
# This is a comment
```

---

## Multi-Line Comments

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

# ✅ Smart Integer Division

If both operands are integers, the transpiler automatically converts `/` into integer division `//`.

### C

```c
a = b / c;
```

### Python

```python
a = b // c
```

---

# ✅ Array & Matrix Initialization

Supports:

- 1D arrays
- 2D arrays
- Matrix initialization

### C

```c
int arr[5];
```

### Python

```python
arr = [0 for _ in range(5)]
```

---

### C

```c
int matrix[3][3];
```

### Python

```python
matrix = [[0 for _ in range(3)] for _ in range(3)]
```

---

# ✅ Block Tracking

Automatically inserts block-ending comments for readability.

### Python

```python
# end block
```

---

# 🧠 Smart Parsing Features

The transpiler includes:

- Regex-based syntax parsing
- Condition transformation
- Operator replacement
- Intelligent indentation handling
- Block stack tracking
- Automatic Python formatting
- Dynamic type stripping

---

# 🎨 Modern Streamlit IDE Interface

The project now includes a completely redesigned developer-style UI.

---

# ✨ UI Features

## ✅ Monaco/VSCode Style Code Editor

Powered by:

- Streamlit-ace
- Syntax highlighting
- Auto-indentation
- Code wrapping
- Dark theme editor

---

## ✅ Modern Cyberpunk UI

Includes:

- Animated gradient background
- Glassmorphism panels
- Interactive buttons
- Responsive layout
- Gradient typography
- Hover animations

---

## ✅ Live File Upload

Supports direct `.c` file upload from the browser.

---

## ✅ Download Generated Python File

Users can instantly download:

```bash
output.py
```

---

## ✅ Conversion Metrics Dashboard

Displays:

- Number of C lines
- Number of Python lines
- Conversion ratio
- Estimated accuracy
- Execution speed

---

## ✅ IDE-Style Layout

The UI includes:

- Split-pane editor
- Sidebar navigation
- Feature panels
- Footer section
- Syntax-highlighted output

---

# 📂 Project Structure

```bash
project/
 ┣ converter.py
 ┣ app.py
 ┣ README.md
 ┣ input.c
 ┗ output.py
```

---

# 🛠️ Technologies Used

## Backend

- Python
- Regex Parsing
- File Handling
- String Manipulation

---

## Frontend

- Streamlit
- streamlit-ace
- Custom CSS
- Glassmorphism UI
- Animated gradients

---

# 📦 Installation

## Clone Repository

```bash
git clone <repository-url>
cd project-folder
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

---

# 📸 Application Features

The application supports:

- Live C code editing
- Instant Python generation
- File upload/download
- Syntax highlighting
- Responsive IDE interface
- Interactive metrics
- Modern developer dashboard

---

# ⚙️ Assumptions

- Input C code is assumed to be syntactically correct
- The transpiler handles a subset of the C language
- Semantic analysis is limited
- Memory management conversion is not included

---

# 🚀 Future Improvements

Planned future upgrades include:

- Pointer support
- Struct conversion
- Switch-case conversion
- Better parser architecture
- Tokenizer + AST generation
- Semantic analysis
- Error reporting system

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Compiler design concepts
- Parsing strategies
- Source-to-source transpilation
- Programming language translation
- Regex-based syntax conversion

---

# 📌 Conclusion

The **C to Python Transpiler** successfully converts core C programming constructs into equivalent Python syntax while preserving readability and logical flow.

Combined with its modern Streamlit-powered IDE interface, the project serves as:

- An educational compiler-design project
- A beginner-friendly transpiler
- A syntax translation demonstration

The project provides a strong foundation for future expansion into advanced compiler and transpiler systems.