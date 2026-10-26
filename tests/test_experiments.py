"""Integration tests of real C compilation and local behavioral comparison."""
import json
from pathlib import Path
import shutil
import uuid
import unittest

from optilab.experiments import run_experiment, toolchains


class CompilerExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = next((item['path'] for item in toolchains() if item['available']), None)
        if cls.compiler is None:
            raise unittest.SkipTest('GCC or Clang is required for compiler integration tests.')

    def setUp(self):
        self.test_root = (Path(__file__).resolve().parents[1] / '.optilab' / 'test-runs').resolve()
        self.directory = self.test_root / uuid.uuid4().hex
        self.directory.mkdir(parents=True)
        self.addCleanup(self.cleanup_directory)

    def cleanup_directory(self):
        target = self.directory.resolve()
        if not target.is_relative_to(self.test_root) or target == self.test_root:
            raise RuntimeError('Refusing cleanup outside test workspace.')
        shutil.rmtree(target)

    def experiment(self, original, candidate, **options):
        return run_experiment(original, candidate, compiler=self.compiler, artifact_root=self.directory, repetitions=options.pop('repetitions', 1), **options)

    def test_equivalent_unsigned_arithmetic_preserves_cases_and_artifacts(self):
        original = '#include <stdio.h>\nint main(void) { unsigned x; if (scanf("%u", &x) != 1) return 2; printf("%u\\n", x + x); return 0; }'
        candidate = original.replace('x + x', '2u * x')
        report = self.experiment(original, candidate, cases=[{'label': 'zero', 'stdin': '0\n', 'args': []}, {'label': 'ordinary', 'stdin': '41\n', 'args': []}], repetitions=2)
        self.assertEqual(report['status'], 'tested_equal')
        self.assertEqual(report['cases'][1]['original'][0]['stdout'].splitlines(), ['82'])
        self.assertTrue(all(case['comparison']['equal'] for case in report['cases']))
        self.assertTrue(report['compiler']['version'])
        self.assertTrue(report['measurements']['includes_process_startup'])
        self.assertEqual(report['measurements']['by_case'][0]['original']['sample_count'], 2)
        for name in ('original', 'candidate'):
            self.assertTrue(Path(report['builds'][name]['artifacts']['assembly']).is_file())
            self.assertTrue(Path(report['sources'][name]['path']).is_file())
        saved = json.loads(Path(report['artifacts']['report']).read_text(encoding='utf-8'))
        self.assertEqual(saved['run_id'], report['run_id'])
        self.assertNotEqual(report['sources']['original']['sha256'], report['sources']['candidate']['sha256'])

    def test_changed_stdout_is_a_counterexample(self):
        original = '#include <stdio.h>\nint main(void) { puts("original"); return 0; }'
        candidate = original.replace('original', 'candidate')
        report = self.experiment(original, candidate)
        self.assertEqual(report['status'], 'counterexample')
        self.assertEqual(report['cases'][0]['comparison']['fields_differing'], ['stdout'])
        self.assertIsNone(report['measurements']['by_case'][0]['median_ratio_original_over_candidate'])

    def test_raw_output_bytes_are_compared_before_lossy_decoding(self):
        original = '#include <stdio.h>\nint main(void) { putchar(254); return 0; }'
        candidate = original.replace('254', '255')
        report = self.experiment(original, candidate)
        self.assertEqual(report['status'], 'counterexample')
        case = report['cases'][0]
        self.assertEqual(case['original'][0]['stdout'], case['candidate'][0]['stdout'])
        self.assertNotEqual(case['original'][0]['stdout_sha256'], case['candidate'][0]['stdout_sha256'])

    def test_exit_codes_and_stderr_are_observable(self):
        original = '#include <stdio.h>\nint main(void) { fputs("left", stderr); return 1; }'
        candidate = original.replace('left', 'right').replace('return 1', 'return 2')
        report = self.experiment(original, candidate)
        self.assertEqual(report['status'], 'counterexample')
        self.assertEqual(set(report['cases'][0]['comparison']['fields_differing']), {'stderr', 'returncode'})

    def test_invalid_c_saves_diagnostics_without_execution(self):
        report = self.experiment('int main(void) { return 0; }', 'this is not a C program;')
        self.assertEqual(report['status'], 'compile_error')
        self.assertFalse(report['builds']['candidate']['success'])
        self.assertTrue(report['builds']['candidate']['compile']['stderr'])
        self.assertEqual(report['cases'], [])
        self.assertTrue(Path(report['artifacts']['report']).is_file())

    def test_nontermination_is_inconclusive_and_stops_repeating(self):
        infinite = 'int main(void) { volatile unsigned x = 0; for (;;) { ++x; } }'
        report = self.experiment(infinite, infinite, timeout=0.1, repetitions=3)
        self.assertEqual(report['status'], 'inconclusive')
        for name in ('original', 'candidate'):
            self.assertEqual(len(report['cases'][0][name]), 1)
            self.assertTrue(report['cases'][0][name][0]['timed_out'])
        self.assertIsNone(report['cases'][0]['comparison']['equal'])

    def test_arguments_are_passed_literally_without_a_shell(self):
        source = '#include <stdio.h>\nint main(int argc, char **argv) { if (argc != 2) return 2; puts(argv[1]); return 0; }'
        argument = 'spaces & ; $(not-a-command)'
        report = self.experiment(source, source, cases=[{'label': 'literal argument', 'stdin': '', 'args': [argument]}])
        self.assertEqual(report['status'], 'tested_equal')
        self.assertEqual(report['cases'][0]['original'][0]['stdout'].splitlines(), [argument])

    def test_missing_compiler_is_reported_without_execution(self):
        source = 'int main(void) { return 0; }'
        report = run_experiment(source, source, compiler=str(self.directory / 'missing-gcc.exe'), artifact_root=self.directory)
        self.assertEqual(report['status'], 'unavailable')
        self.assertEqual(report['cases'], [])
        self.assertEqual(report['builds'], {})
        self.assertTrue(Path(report['sources']['original']['path']).is_file())
        self.assertTrue(Path(report['artifacts']['report']).is_file())

    def test_each_run_has_an_isolated_directory(self):
        source = 'int main(void) { return 0; }'
        first = self.experiment(source, source)
        second = self.experiment(source, source)
        self.assertNotEqual(first['run_id'], second['run_id'])
        self.assertNotEqual(first['artifacts']['directory'], second['artifacts']['directory'])


class InputValidationTests(unittest.TestCase):
    def test_shell_flags_and_malformed_inputs_are_rejected(self):
        source = 'int main(void) { return 0; }'
        for options in ({'optimization': '-O2; echo bad'}, {'optimization': []}, {'repetitions': True}, {'timeout': float('nan')}, {'cases': []}, {'cases': [{'args': 'not a list'}]}, {'compiler': 'python'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                run_experiment(source, source, **options)


if __name__ == '__main__':
    unittest.main()
