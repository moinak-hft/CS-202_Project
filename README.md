# OptiLab — compiler optimization experiments

OptiLab extends the original CS202 C optimization visualizer into a local tool for tracing transformations and testing optimization hypotheses. It has two connected workflows:

- **Trace a supported C program:** inspect each optimization pass, emitted C, reasons and per-function control flow.
- **Investigate two source variants:** compile both with the same settings, compare observed behavior over input cases, collect assembly/compiler diagnostics, and save a reproducible report.

The original optimizer and README are preserved in `legacy/`. The implementation is shared by the CLI and web interface; importing it performs no parsing, rendering or program execution.

## Run

For a fresh source checkout, install the dependencies in a virtual environment before starting the app. The commands below assume the cloned repository folder is named `CS-202_Project`; dependencies are installed locally rather than bundled in the repository.

Python 3.11 or newer is recommended. The tested environment used Python 3.14, Flask 3.1.3, pycparser 3.12 and GCC 15.1 on Windows.

PowerShell:

```powershell
cd CS-202_Project
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m optilab serve
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The app binds to localhost with debug mode off. To use a different port: `python -m optilab serve --port 5050`.

On macOS/Linux use `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt` and `.venv/bin/python -m optilab serve`.

A GCC or Clang executable on PATH is needed for compiler experiments. Pure analysis does not need a compiler or Graphviz. Check discovery with `python -m optilab toolchains`. An explicit compiler executable can also be selected in the CLI.

The interface runs submitted programs only when **Run behavioral comparison** is clicked. It is a local developer tool for code you trust, not a sandbox for public/untrusted code. Timeouts limit execution duration; they do not isolate operating-system access. Do not expose this development server publicly.

## Try the first investigation

1. Select **Constant pipeline**, trace its passes, and inspect the emitted candidate and change reasons.
2. Open the CFG tab. Return, break and continue edges have explicit destinations.
3. Run a comparison. Matching output and return values produce **Tested equal**, with the precise recorded input cases.
4. For a production compiler experiment, load `examples/vectorization_original.c` as original and `examples/vectorization_candidate.c` as candidate. The candidate removes a noinline constraint; the computation is unchanged.
5. Use input cases from `examples/experiment_cases.json`. Inspect the generated assembly, compiler optimization reports and process timing distributions. Compiler choices are measured, not assumed.

The array-based vectorization examples intentionally use the production compiler workflow. They exceed the custom optimizer's scalar subset, so the trace workflow reports them as unsupported rather than guessing.

The experiment may or may not enable vectorization or improve runtime on a particular compiler/target. A report showing no improvement is a valid result.

## Command line

Use the virtual environment's Python for these commands, or activate that environment first.

```powershell
python -m optilab analyze examples/constant_pipeline.c --output .optilab/candidate.c --report .optilab/trace.json --cfg .optilab/graphs.json
python -m optilab experiment examples/vectorization_original.c examples/vectorization_candidate.c --compiler gcc --optimization=-O3 --cases examples/experiment_cases.json --repetitions 5
python -m unittest discover -s tests -v
```

Use the equals sign in `--optimization=-O3`, because the value begins with a dash. Commands use paths relative to the current directory; the web app locates its own templates/examples independently of the working directory.

`python main.py` also starts the interface. `python optimiser.py examples/constant_pipeline.c` is a compatibility entrypoint that prints transformed C. Neither optimizer copy contains duplicated transformation logic.

Analysis supports `--passes propagation folding dce unused` and `--max-iterations 8`. Reported pass times cover transformation work; they exclude graph rendering and compilation.

Experiment exit codes: 0 = tested equal, 1 = behavioral counterexample, 2 = unavailable/inconclusive/compile error/invalid input. The CLI prints the run identifier and artifact paths. Cases are JSON objects with `label`, `stdin` and a string `args` array.

## What is implemented

### Experimental source transformer

- Lexically scoped scalar identities and independent per-function propagation facts.
- Conservative loop handling: modified loop facts are invalidated before analyzing the loop.
- Typed 32-bit signed/unsigned constant folding, truncation-toward-zero division/remainder, wrapping unsigned arithmetic, and guards against folding signed overflow or invalid operations.
- List-aware AST replacement, including function-call arguments.
- Branch-aware backward liveness for unused local assignments.
- Fixed-point pass execution, C emission, source-linked change reasons and structured diagnostics.
- Structural per-function CFGs and structured AST output without Graphviz.

Supported source data are local/parameter `int` and `unsigned int`, structured control flow and conservative direct function calls. The implementation assumes 32-bit int/unsigned int and is not a complete C type checker.

Pointers, arrays, globals, volatile/atomic data, structs, unsupported widths and complex preprocessing receive explicit diagnostics. Only leading stdio.h and stdlib.h includes are accepted; declarations/macros are not fully semantically analyzed. Other headers, line continuations and trigraph preprocessing receive diagnostics. The compiler experiment backend accepts programs beyond this subset, subject to the selected real compiler.

The API explicitly reports unsupported programs. A successful transformation is not by itself a proof of equivalence.

### Compiler experiment backend

- Auto-discovered GCC/Clang or explicit executable, with recorded version/target.
- UUID run directories and identical optimization settings for both variants.
- Complete commands, source hashes, compiler diagnostics and assembly.
- GCC optimization reports; optional Clang optimization records and LLVM IR.
- Finite behavioral comparison using raw stdout/stderr hashes and exit status.
- Compile/run timeouts, repeated process measurements and structured JSON reports.
- Separate tested-equal, counterexample, compile-error, inconclusive and compiler-unavailable results.
- Downloadable source, report, assembly and diagnostic artifacts.

Clang-specific integration is included but was not exercised on this machine because Clang is not installed. GCC is the tested backend.

## Interpreting evidence

**Tested equal** means that both variants produced matching observable results on the recorded finite cases. It is not a universal correctness claim. Avoid undefined-behavior input programs when interpreting comparisons. Crashes/timeouts are reported separately rather than treated as successful matching behavior.

Timings measure complete process wall time, including process startup, input/output and program work. They are useful for substantial repeated workloads and rough comparisons, not precise per-kernel profiling. The interface labels this limitation. Do not interpret a tiny timing ratio as a demonstrated speedup.

A source-node reduction does not establish faster machine code. Compare variants with the same compiler, target and optimization level. Candidate interventions such as restrict contracts or relaxed floating-point settings require explicit semantic conditions; they are not universally safe fixes.

## Layout

```text
optilab/optimizer.py        shared subset transformer and pass trace
optilab/cfg.py              structural per-function CFG and AST data
optilab/experiments.py      compiler runner, comparison and evidence
optilab/__main__.py         CLI
WebInstance/               local Flask app and interface
examples/                  regression and compiler experiment inputs
tests/                     unittest regressions and compiler/web checks
legacy/                    original optimizer and README
.optilab/runs/<run-id>/     generated evidence (ignored by Git)
```

Tests use the standard library unittest runner. Compiler integration tests skip if no suitable compiler is available; Flask tests require the requirements above.

## Next capabilities

The implemented milestone is a working experiment foundation. Future work can add first-failing-pass localization, failure reduction, richer compiler remark/source linking, bounded verification and learned experiment selection.

No ML model or formal-equivalence checker is claimed in this release. Those features should build on collected, measured evidence rather than inferred labels. LLVM optimization remarks, Compiler Explorer, MLGO and Alive2 are relevant prior art; the longer-term goal is a connected experiment-to-evidence workflow.

## Original team

Shobhit Gupta, Shubham, Tanish Kumar, Moinak Goswami and Abhijit Kamble. See `legacy/README.md` for the original course-project description.
