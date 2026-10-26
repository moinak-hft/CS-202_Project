# Validation record

Validated on 25 October 2026 with Python 3.14.4, Flask 3.1.3, pycparser 3.12 and GCC 15.1 (MSYS2 MinGW) on Windows.

- Final suite: **42 unittest tests passed**, 41.418 seconds.
- Optimizer tests include 28 source/order differential fixtures, compiled as original and transformed C (56 compilations).
- Independent review additionally compared 35 scalar/control-flow cases across 5 inputs (175 observations); all recorded behavior matched.
- CFG regressions check return termination, break/continue destinations, for-loop increments, unreachable statements and separate functions.
- Compiler tests cover matching outputs, counterexamples, invalid C, nontermination, unavailable compilers, raw binary output comparisons, literal argument handling and isolated artifacts.
- Web tests cover shared-core analysis, explicit execution, request validation, source limits, origin handling and confined artifact downloads.
- Actual headless Chrome rendered desktop/mobile layouts. Browser requests were bridged to the real Flask test client because direct loopback navigation was blocked in the browser's managed environment. Real GCC compilation/execution and report downloads were exercised through that bridge. JavaScript syntax and interaction smoke checks passed.
- No helper server or browser process is left running.

## Saved production-compiler experiment

The report in `evidence/inlining-example/` records a real GCC -O3 comparison between the supplied noinline helper example and the candidate that allows inlining.

Both variants matched stdout, stderr and exit status for arguments 0, 1 and 400. GCC's candidate report shows vectorization of the inner array-update loop. Commands, source, assembly and optimization reports are preserved.

Timing data are process wall times including startup. They are not a stable kernel speedup claim. The recorded report paths identify where the experiment actually ran before deployment.

## Limits

Finite matching tests do not prove semantic equivalence. The custom transformer supports a documented scalar subset and rejects unsupported features. The compiler backend executes trusted local programs and is not an operating-system sandbox.

Clang-specific output collection is implemented but untested on this machine because Clang is unavailable. No ML model or formal-equivalence checker is included in this milestone.
