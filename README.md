# C-to-CFG Analyzer & Optimizer

A robust static analysis and optimization pipeline that converts raw C source code into optimized Control Flow Graphs (CFGs). This repository is built entirely on a high-performance, low-level backend leveraging modern C++ and the LLVM/Clang compiler infrastructure. 

## Project Architecture & LLVM Theory

This project relies on the modular architecture of the LLVM compiler framework, operating primarily at the frontend (Clang) and middle-end (LLVM Pass Infrastructure) to perform code analysis and transformation without relying on an interpreter.

### 1. The Clang Frontend & AST Traversal
The first stage of the pipeline avoids manual parsing by hooking directly into Clang's powerful parsing libraries. 
* **Lexing & Parsing:** Raw C code is tokenized and parsed into a highly detailed Abstract Syntax Tree (AST). 
* **RecursiveASTVisitor:** Instead of linear text processing, the analyzer utilizes Clang's `RecursiveASTVisitor` to traverse the AST hierarchy. By inspecting specific `Stmt` (Statement) and `Expr` (Expression) nodes, the system identifies control-flow divergence (e.g., `if`, `for`, `while`, `goto`) to accurately demarcate the boundaries of Basic Blocks.

### 2. LLVM Intermediate Representation (IR) & Pass Infrastructure
Once control flow is mapped, the architecture shifts to analyzing the flow of data.
* **Pass Manager:** The static analysis and optimization algorithms are implemented as modular "Passes." This allows analyses (like Reaching Definitions) to be chained and executed sequentially, feeding their results into transformation passes (like Dead Code Elimination).
* **Static Single Assignment (SSA):** A critical theoretical component of this project is the transformation into SSA form (`SSA_Transformation.cpp`). In SSA, every variable is assigned exactly once. This drastically simplifies data-flow analysis, as properties like use-def chains become explicit and $\phi$-nodes (phi-nodes) map exactly how divergent control flow paths merge data back together.

### 3. Dominance & Graph Theory
Optimizations require strict mathematical proofs of execution order.
* **Dominator Trees:** The `DominatorTreePass.cpp` constructs a tree where a node *A* dominates node *B* if every path from the entry node to *B* must go through *A*. This strict mathematical hierarchy is what allows the pipeline to safely identify loop-invariant code and compute strict dominance frontiers necessary for SSA construction.

## Implemented Features

### Phase 1: CFG Construction
* Parses raw C code to generate an Abstract Syntax Tree (AST) using Clang libraries.
* Segments instructions into strict Basic Blocks (single entry, single exit).
* Constructs the directed Control Flow Graph mapped from the Basic Blocks.

### Phase 2: Static Analysis
* **Reaching Definitions Analysis:** Tracks variable assignments throughout the CFG to detect potential bugs like uninitialized variables.
* **Live Variable Analysis:** Determines if a variable's current value will be read in the future, forming the foundation for safe code deletion.

### Phase 3: Optimizations
* **Constant Folding & Propagation:** Resolves deterministic calculations at compile-time and propagates the resulting constants forward.
* **Dead Code Elimination (DCE):** Utilizes Live Variable Analysis to strip away instructions that do not impact the program's final state.
* **Unreachable Code Removal:** Employs DFS/BFS graph traversal to identify and prune orphaned nodes without a valid entry path.

### Advanced Transformations
* **Dominator Trees & Loop Detection:** Custom LLVM pass to calculate dominance frontiers and detect loop invariants.
* **Graph Visualization:** Exports the final optimized structures into `.dot` format, rendering the basic blocks and branch edges visually via Graphviz.

## Prerequisites

This project is configured for a native Linux environment.

* Pure Linux Environment (Ubuntu/Debian recommended)
* CMake (>= 3.10)
* LLVM / Clang framework (`sudo apt install llvm clang libclang-dev`)
* C++17 or higher compliant compiler (GCC or Clang)
* Graphviz (For `.dot` file rendering)

## Build and Run

The build system utilizes CMake to link against the massive LLVM and Clang static libraries. 

```bash
mkdir build
cd build
cmake ..
make
./CFGAnalyzer <input_file.c>
```

**Authors:**
1. Shobhit Gupta 2024CSB1155
2. Shubham _ 2024CSB1157
3. Tanish Kumar 2024CSB1161
4. Moinak Goswami 2024CSB1225
5. Abhijit Kishan Kamble 2024CSB1401
