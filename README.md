# C-to-CFG Analyzer & Optimizer

A robust static analysis and optimization pipeline that converts raw C source code into optimized Control Flow Graphs (CFGs). This repository implements a dual-approach architecture: a rapid-prototyping frontend in Python and a high-performance, low-level backend leveraging C++ and the LLVM infrastructure.

## Project Architecture

The codebase is split into two primary methodologies to satisfy different performance and prototyping needs:

* **C++ / LLVM Core:** Utilizes the Clang frontend and LLVM passes (`CFGAnalyzer.cpp`, `DominatorTreePass.cpp`, `SSA_Transformation.cpp`) for deep AST traversal, strict memory management, and advanced graph transformations.
* **Python Prototype:** Uses `pycparser` and `NetworkX` (`cfg_builder.py`, `main.py`) for rapid graph manipulation and algorithm verification.

## Implemented Features

### Phase 1: CFG Construction
* Parses raw C code to generate an Abstract Syntax Tree (AST).
* Segments instructions into strict Basic Blocks (single entry, single exit).
* Constructs the directed Control Flow Graph mapped from the Basic Blocks.

### Phase 2: Static Analysis
* **Reaching Definitions Analysis:** Tracks variable assignments throughout the CFG to detect potential bugs like uninitialized variables.
* **Live Variable Analysis:** Determines if a variable's current value will be read in the future, forming the foundation for safe code deletion.

### Phase 3: Optimizations
* **Constant Folding & Propagation:** Resolves deterministic calculations at compile-time and propagates the resulting constants forward.
* **Dead Code Elimination (DCE):** Utilizes Live Variable Analysis to strip away instructions that do not impact the program's final state.
* **Unreachable Code Removal:** Employs DFS/BFS graph traversal to identify and prune orphaned nodes without a valid entry path.

### Advanced & Bonus Optimizations
* **Dominator Trees & Loop Detection:** Custom LLVM pass (`DominatorTreePass.cpp`) to calculate dominance frontiers and detect loop invariants.
* **Static Single Assignment (SSA):** Transforms the CFG into SSA form (`SSA_Transformation.cpp`) to simplify data flow analysis.
* **Graph Visualization:** Exports the final optimized structures into `.dot` format, rendering the basic blocks and branch edges visually via Graphviz (`visualize.py`).

## Prerequisites

**For the C++ (LLVM) Pipeline:**
* CMake (>= 3.10)
* LLVM / Clang framework
* C++17 or higher compliant compiler

**For the Python Prototype:**
* Python 3.8+
* Graphviz (System-level installation required for rendering)

## Build and Run

### C++ LLVM Build Pipeline
```bash
mkdir build
cd build
cmake ..
make
./CFGAnalyzer <input_file.c>

Author's:
1. Shobhit Gupta 2024CSB1155
2. Shubham _ 2024CSB1157
3. Tanish Kumar 2024CSB1161
4. Moinak Goswami 2024CSB1225
5. Abhijit Kishan Kamble 2024CSB1401
