"""Command-line entrypoint for analysis, compiler experiments and the local UI."""
import argparse
import json
from pathlib import Path
import sys

def _read(path):
    return Path(path).read_text(encoding="utf-8-sig")

def _write(path, content):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def main(argv=None):
    parser = argparse.ArgumentParser(prog="optilab", description="Trace C transformations and run reproducible compiler experiments.")
    sub = parser.add_subparsers(dest="command")
    analyze = sub.add_parser("analyze", help="Transform a supported scalar C program; never execute it.")
    analyze.add_argument("source")
    analyze.add_argument("-o", "--output")
    analyze.add_argument("--report")
    analyze.add_argument("--cfg", help="Save structured original/candidate CFG data.")
    analyze.add_argument("--passes", nargs="+", choices=("propagation", "folding", "dce", "unused"))
    analyze.add_argument("--max-iterations", type=int, default=8)
    experiment = sub.add_parser("experiment", help="Compile and execute two local C variants.")
    experiment.add_argument("original")
    experiment.add_argument("candidate")
    experiment.add_argument("--compiler")
    experiment.add_argument("--optimization", choices=("-O0", "-O1", "-O2", "-O3", "-Os", "-Oz", "-Og"), default="-O2",
                            help="Use equals syntax, e.g. --optimization=-O3.")
    experiment.add_argument("--cases", help="JSON array of {label, stdin, args} input cases.")
    experiment.add_argument("--repetitions", type=int, default=3)
    experiment.add_argument("--timeout", type=float, default=2.0)
    experiment.add_argument("--artifacts", default=".optilab/runs")
    experiment.add_argument("--report", help="Also copy the structured report to this path.")
    sub.add_parser("toolchains", help="List discovered GCC/Clang compilers.")
    serve = sub.add_parser("serve", help="Open a local investigation interface.")
    serve.add_argument("--port", type=int, default=5000)
    args = parser.parse_args(argv)
    try:
        if args.command in (None, "serve"):
            port = getattr(args, "port", 5000)
            if not 1 <= port <= 65535:
                parser.error("port must be between 1 and 65535")
            from WebInstance.app import app
            print(f"OptiLab: http://127.0.0.1:{port}")
            app.run(host="127.0.0.1", port=port, debug=False)
            return 0
        if args.command == "toolchains":
            from .experiments import toolchains
            print(json.dumps(toolchains(), indent=2))
            return 0
        if args.command == "analyze":
            from .optimizer import optimize_source
            result = optimize_source(_read(args.source), pass_order=args.passes, max_iterations=args.max_iterations)
            if args.report:
                _write(args.report, json.dumps(result, indent=2) + "\n")
            for item in result["diagnostics"]:
                print(f'{item["severity"]}: {item["message"]}', file=sys.stderr)
            if result["status"] != "ok":
                return 2
            if args.output:
                _write(args.output, result["optimized_code"])
            else:
                print(result["optimized_code"], end="")
            if args.cfg:
                from .cfg import build_cfg, build_ast
                graphs = dict(original=build_cfg(result["original_code"]), candidate=build_cfg(result["optimized_code"]),
                              ast=build_ast(result["optimized_code"]))
                _write(args.cfg, json.dumps(graphs, indent=2) + "\n")
            return 0
        from .experiments import run_experiment
        cases = json.loads(_read(args.cases)) if args.cases else None
        report = run_experiment(_read(args.original), _read(args.candidate), compiler=args.compiler,
                                optimization=args.optimization, cases=cases, repetitions=args.repetitions,
                                timeout=args.timeout, artifact_root=Path(args.artifacts))
        if args.report:
            _write(args.report, json.dumps(report, indent=2) + "\n")
        print("Result:", report["status"])
        print("Run:", report.get("run_id", "unavailable"))
        print("Artifacts:", report.get("artifacts", {}))
        print("Matching finite tests are evidence, not an equivalence proof. Timings include process startup.")
        return 0 if report["status"] == "tested_equal" else (1 if report["status"] == "counterexample" else 2)
    except (OSError, ValueError, ImportError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
