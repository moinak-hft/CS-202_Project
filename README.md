# C Language Compiler Optimization Pipeline

A source-level compiler optimization framework for C programs built using Python, `pycparser`, `NetworkX`, and `Graphviz`.

This project parses C source code into an Abstract Syntax Tree (AST), applies multiple classical compiler optimizations iteratively, and generates visual Control Flow Graphs (CFGs) to show how the program evolves through each optimization stage.

Along with the compiler optimizer, we also developed a simple web application that demonstrates the same optimization pipeline visually through a website interface for easier understanding and interaction.

---

# Project Overview

Modern compilers perform multiple optimization passes to improve performance, simplify execution flow, and remove unnecessary computations before generating machine code.

This project recreates a simplified version of that optimization pipeline at the source-code level.

The system:

- Parses C code into an AST
- Applies multiple optimization passes
- Repeats optimization passes until convergence
- Generates CFG images after every stage
- Produces a final optimized CFG and pipeline graph

The project demonstrates how real compiler optimization passes interact with each other and how one optimization can expose opportunities for another.

---

# Features

## Iterative Optimization Pipeline

Instead of performing only one optimization pass, the system repeatedly applies optimizations until the program reaches a fixed point.

Pipeline Flow:

```text
Constant Propagation
        ↓
Constant Folding
        ↓
Dead Code Elimination
        ↓
Repeat Until Stable
        ↓
Unused Assignment Elimination
        ↓
Final Optimized CFG
```

---

## AST Visualization

The project generates an AST graph (`ast.png`) directly from the parsed C program.

This helps visualize:
- Program structure
- Expressions
- Loops
- Branches
- Function bodies

---

## Automatic CFG Generation

After every optimization pass, a new CFG image is generated showing how the control flow changes during optimization.

Generated outputs include:

- Original CFG
- CFG after propagation
- CFG after folding
- CFG after dead code elimination
- Final optimized CFG
- Complete optimization pipeline graph

---

## Compiler Optimization Passes

### Constant Propagation

Tracks variables with known constant values and replaces their usages.

Example:

```c
int a = 5;
int b = a + 2;
```

becomes:

```c
int b = 5 + 2;
```

---

### Constant Folding

Evaluates constant expressions during compile time.

Example:

```c
3 + 5
```

becomes:

```c
8
```

---

### Dead Code Elimination (DCE)

Removes unreachable or unnecessary code.

Example:

```c
if (0) {
    ...
}
```

is removed completely.

---

### Unused Assignment Elimination (UAE)

Eliminates assignments whose values are never used later in the program.

---

## Fixed Point Optimization

The optimizer automatically stops when the AST stops changing, ensuring that no unnecessary iterations are performed.

---

## Simple Web Application

We also developed a lightweight website that demonstrates the same optimization pipeline visually.

The web app allows users to:
- Input C code
- Run optimizations
- View generated CFGs
- Understand optimization stages interactively

This makes the project easier to explore and more accessible for learning compiler design concepts.

---

# Why This Project Is Useful

Compiler optimization is one of the most important areas in compiler design and systems programming.

This project helps in understanding:

- How compilers simplify programs
- How optimization passes interact
- Why multiple optimization passes are required
- How CFGs represent execution flow
- How static analysis works internally
- How unreachable or redundant code is detected

It acts as an educational mini-compiler framework for learning:

- Compiler Design
- Program Analysis
- CFG Construction
- AST Traversal
- Static Optimization Techniques

---

# Technologies Used

- Python
- pycparser
- NetworkX
- Graphviz
- pydot
- Regular Expressions (`re`)

---

# Generated Outputs

| File | Description |
|---|---|
| `ast.png` | AST visualization |
| `cfg_original.png` | Original CFG |
| `cfg_iter_X_prop.png` | CFG after propagation |
| `cfg_iter_X_fold.png` | CFG after folding |
| `cfg_iter_X_dce.png` | CFG after DCE |
| `cfg_optimized.png` | Final optimized CFG |
| `pipeline_graph.png` | Complete optimization pipeline |

---

# How It Works

## 1. Preprocessing

The input C program is cleaned by:
- Removing comments
- Replacing simple macros
- Removing `#include` directives

---

## 2. Parsing

The cleaned program is parsed into an AST using `pycparser`.

---

## 3. Optimization Passes

The optimizer repeatedly applies:
- Constant Propagation
- Constant Folding
- Dead Code Elimination

until no more changes occur.

---

## 4. Final Cleanup

Unused Assignment Elimination removes assignments whose results are never used.

---

## 5. CFG Generation

A CFG is generated after every optimization stage for visualization purposes.

---

# Example Optimization Flow

```text
Original Code
      ↓
Constant Propagation
      ↓
Constant Folding
      ↓
Dead Code Elimination
      ↓
Repeat Until Stable
      ↓
Unused Assignment Elimination
      ↓
Final Optimized CFG
```

---

# Known Limitations

- Limited macro preprocessing support
- No support for:
  - `goto`
  - `switch-case` fallthrough
  - function pointers
  - advanced preprocessor directives
- Optimizations are intraprocedural only
- Conservative loop analysis
- Integer-only constant folding

---

# Running the Project

Install dependencies:

```bash
pip install pycparser networkx graphviz pydot
```

Run the optimizer:

```bash
python main.py
```

Make sure your input C file is available as:

```text
debug.c
```

---

#  Team Members

- Shubham
- Shobhit Gupta
- Abhijit Kamble
- Tanish Kumar
- Moinak Goswami

---

#  Project Report

Detailed implementation and optimization explanations are included in the project report.

---