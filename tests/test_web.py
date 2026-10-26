"""HTTP contract and artifact confinement tests for the local Flask interface."""
import importlib.util
import json
from pathlib import Path
import shutil
import uuid
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("optilab_web", ROOT / "WebInstance" / "app.py")
web = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(web)

class WebTests(unittest.TestCase):
    def setUp(self):
        self.temporary = ROOT / ".optilab" / "test-web" / uuid.uuid4().hex
        self.temporary.mkdir(parents=True)
        self.addCleanup(self.cleanup_directory)
        web.app.config.update(TESTING=True, RUNS_DIR=self.temporary)
        self.client = web.app.test_client()

    def cleanup_directory(self):
        target = self.temporary.resolve()
        parent = (ROOT / ".optilab" / "test-web").resolve()
        if target.parent != parent:
            raise RuntimeError("Refusing cleanup outside the web test directory")
        shutil.rmtree(target)
    def test_workspace_renders_without_compiling(self):
        with patch.object(web, "run_experiment") as runner:
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Trace optimizations", response.data)
        self.assertIn(b"Candidate C", response.data)
        runner.assert_not_called()

    def test_analysis_rejects_non_json_and_missing_source(self):
        self.assertEqual(self.client.post("/api/analyze", data="int main(){}").status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", json={}).status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", json={"source":"int main(){return 0;}","passes":"folding"}).status_code, 400)

    def test_trace_uses_shared_optimizer_and_cfg(self):
        result = dict(status="ok", diagnostics=[], original_code="original", optimized_code="candidate", trace=[], metrics={})
        with patch.object(web, "optimize_source", return_value=result) as optimize, patch.object(web, "build_cfg", return_value={"functions":[]}) as graph:
            response = self.client.post("/api/analyze", json={"source":"int main(){return 0;}","passes":["folding"]})
        self.assertEqual(response.status_code, 200)
        optimize.assert_called_once_with("int main(){return 0;}", pass_order=["folding"])
        self.assertEqual(graph.call_count, 2)
        self.assertEqual(set(response.json["graphs"]), {"original","candidate"})

    def test_unsupported_source_keeps_diagnostics(self):
        with patch.object(web, "optimize_source", return_value={"status":"unsupported","diagnostics":[{"message":"Pointer unsupported"}]}), patch.object(web, "build_cfg") as graph:
            response = self.client.post("/api/analyze", json={"source":"int *p;"})
        self.assertEqual(response.json["status"], "unsupported")
        graph.assert_not_called()

    def test_execution_requires_explicit_experiment_post(self):
        run_id = "a" * 32
        directory = self.temporary / run_id
        directory.mkdir()
        (directory / "report.json").write_text('{"status":"tested_equal"}', encoding="utf-8")
        result = dict(run_id=run_id, status="tested_equal")
        with patch.object(web, "run_experiment", return_value=result) as runner:
            response = self.client.post("/api/experiment", json={"original":"int main(){return 0;}","candidate":"int main(){return 0;}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(runner.call_args.kwargs["artifact_root"], self.temporary)
        self.assertEqual(response.json["artifact_links"][0]["name"], "report.json")

    def test_cross_origin_execution_is_rejected(self):
        with patch.object(web, "run_experiment") as runner:
            response = self.client.post("/api/experiment", json={"original":"x","candidate":"x"}, headers={"Origin":"https://unrelated.example"})
        self.assertEqual(response.status_code, 403)
        runner.assert_not_called()

    def test_artifacts_only_serve_allowed_files_inside_the_run(self):
        run_id = "b" * 32
        directory = self.temporary / run_id
        directory.mkdir()
        (directory / "report.json").write_text('{"status":"tested_equal"}', encoding="utf-8")
        (directory / "candidate.exe").write_bytes(b"not an executable")
        outside = self.temporary / "outside.txt"
        outside.write_text("private", encoding="utf-8")
        response = self.client.get(f"/api/runs/{run_id}/artifacts/report.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["status"], "tested_equal")
        response.close()
        self.assertEqual(self.client.get(f"/api/runs/{run_id}/artifacts/candidate.exe").status_code, 404)
        self.assertEqual(self.client.get(f"/api/runs/{run_id}/artifacts/../outside.txt").status_code, 404)
        self.assertEqual(self.client.get("/api/runs/not-a-run/artifacts/report.json").status_code, 404)

    def test_compiler_validation_message_is_returned(self):
        with patch.object(web, "run_experiment", side_effect=ValueError("Unknown compiler")):
            response = self.client.post("/api/experiment", json={"original":"x","candidate":"x"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Unknown compiler")

    def test_toolchain_discovery_is_read_only(self):
        with patch.object(web, "toolchains", return_value=[{"name":"gcc","available":True}]), patch.object(web, "run_experiment") as runner:
            response = self.client.get("/api/toolchains")
        self.assertEqual(response.json["toolchains"][0]["name"], "gcc")
        runner.assert_not_called()

    def test_large_requests_get_json_error(self):
        response = self.client.post("/api/analyze", json={"source":"x" * 300_000})
        self.assertEqual(response.status_code, 413)
        self.assertIn("error", response.json)

if __name__ == "__main__":
    unittest.main()
