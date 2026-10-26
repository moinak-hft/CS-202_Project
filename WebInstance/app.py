"""Local OptiLab interface. Source execution is explicit and intended for trusted local code."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import HTTPException
from optilab.optimizer import optimize_source
from optilab.experiments import run_experiment, toolchains
from optilab.cfg import build_cfg

app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent / "templates"), static_folder=str(Path(__file__).resolve().parent / "static"))
app.config.update(MAX_CONTENT_LENGTH=256 * 1024, RUNS_DIR=ROOT / ".optilab" / "runs", TRUSTED_HOSTS=["localhost", "127.0.0.1"])

def payload():
    if not request.is_json:
        raise ValueError("Send an application/json request.")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("The request must be a JSON object.")
    return data

def source_field(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must contain C source code.")
    if len(value) > 100_000:
        raise ValueError(f"{key} is too large (maximum 100,000 characters).")
    return value

@app.before_request
def same_origin():
    if request.method == "POST":
        origin = request.headers.get("Origin")
        if origin and urlsplit(origin).netloc != request.host:
            return jsonify(error="Cross-origin execution requests are not allowed."), 403
    return None

@app.errorhandler(ValueError)
def invalid_request(error):
    return jsonify(error=str(error)), 400

@app.errorhandler(HTTPException)
def http_error(error):
    if request.path.startswith("/api/"):
        return jsonify(error=error.description), error.code
    return error

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify(status="ok", name="OptiLab", mode="local")

@app.get("/api/toolchains")
def available_toolchains():
    return jsonify(toolchains=toolchains())

@app.get("/api/examples")
def examples():
    directory = ROOT / "examples"
    metadata = {}
    manifest = directory / "index.json"
    if manifest.is_file():
        try:
            loaded = json.loads(manifest.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                metadata = loaded
        except (ValueError, OSError):
            pass
    entries = []
    for path in sorted(directory.glob("*.c")):
        entry = metadata.get(path.name, {})
        if not isinstance(entry, dict):
            entry = {}
        example = dict(id=path.name, name=entry.get("name", path.stem.replace("_", " ").title()),
                       description=entry.get("description", ""), code=path.read_text(encoding="utf-8"))
        if path.name.endswith("_original.c"):
            candidate = directory / path.name.replace("_original.c", "_candidate.c")
            if candidate.is_file():
                example["candidate_code"] = candidate.read_text(encoding="utf-8")
        if isinstance(entry.get("cases"), list):
            example["cases"] = entry["cases"]
        entries.append(example)
    return jsonify(examples=entries)

@app.post("/api/analyze")
def analyze():
    data = payload()
    source = source_field(data, "source")
    passes = data.get("passes")
    if passes is not None and (not isinstance(passes, list) or not all(isinstance(p, str) for p in passes)):
        raise ValueError("passes must be a list of pass names.")
    result = optimize_source(source, pass_order=passes)
    graphs = {}
    if result.get("status") == "ok":
        for key, code in (("original", source), ("candidate", result.get("optimized_code", source))):
            try:
                graphs[key] = build_cfg(code)
            except (ValueError, TypeError, AttributeError) as error:
                graphs[key] = dict(functions=[], diagnostic=str(error))
    result["graphs"] = graphs
    return jsonify(result)

@app.post("/api/experiment")
def experiment():
    data = payload()
    original = source_field(data, "original")
    candidate = source_field(data, "candidate")
    compiler = data.get("compiler") or None
    if compiler is not None and not isinstance(compiler, str):
        raise ValueError("compiler must be a toolchain name or executable path.")
    result = run_experiment(
        original, candidate, compiler=compiler, optimization=data.get("optimization", "-O2"),
        cases=data.get("cases"), repetitions=data.get("repetitions", 3),
        timeout=data.get("timeout", 2.0), artifact_root=Path(app.config["RUNS_DIR"]))
    run_id = result.get("run_id")
    if isinstance(run_id, str) and re.fullmatch(r"[0-9a-f]{32}", run_id):
        result["artifact_links"] = list_artifacts(run_id)
        result["report_url"] = f"/api/runs/{run_id}/artifacts/report.json"
    return jsonify(result)

def run_directory(run_id):
    if not re.fullmatch(r"[0-9a-f]{32}", run_id):
        raise ValueError("Invalid run identifier.")
    root = Path(app.config["RUNS_DIR"]).resolve()
    directory = (root / run_id).resolve()
    if directory.parent != root:
        raise ValueError("Invalid run directory.")
    return directory

def list_artifacts(run_id):
    directory = run_directory(run_id)
    allowed = {".json", ".c", ".s", ".ll", ".yaml", ".yml", ".txt"}
    if not directory.is_dir():
        return []
    return [dict(name=path.name, url=f"/api/runs/{run_id}/artifacts/{path.name}")
            for path in sorted(directory.iterdir()) if path.is_file() and path.suffix in allowed
            and path.resolve().parent == directory]

@app.get("/api/runs/<run_id>/artifacts/<path:filename>")
def artifact(run_id, filename):
    try:
        directory = run_directory(run_id)
    except ValueError:
        return jsonify(error="Run not found."), 404
    path = (directory / filename).resolve()
    if path.parent != directory or path.suffix not in {".json", ".c", ".s", ".ll", ".yaml", ".yml", ".txt"} or not path.is_file():
        return jsonify(error="Artifact not found."), 404
    return send_file(path, as_attachment=True, download_name=path.name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
