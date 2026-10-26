"""Semantic regression tests for the supported scalar-C optimizer."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from optilab.optimizer import PASS_NAMES, optimize_source


class OptimizerContractTests(unittest.TestCase):
    def test_json_safe_trace_with_reasons(self):
        result = optimize_source('int f(){int a=5;int b=a+2;if(1){return b;}return 99;}')
        self.assertEqual(result['status'], 'ok', result['diagnostics'])
        json.dumps(result)
        self.assertGreater(result['metrics']['changed_passes'], 0)
        self.assertLess(result['metrics']['optimized_ast_nodes'], result['metrics']['original_ast_nodes'])
        self.assertEqual([item['pass_name'] for item in result['trace'][:4]], list(PASS_NAMES))
        reasons = [change['reason'] for stage in result['trace'] for change in stage['changes']]
        self.assertTrue(reasons)
        self.assertTrue(all(reasons))
        for stage in result['trace']:
            self.assertEqual(stage['changed'], stage['before'] != stage['after'])
            self.assertGreaterEqual(stage['duration_ms'], 0)

    def test_pass_order_validation(self):
        for order in ([], ['unknown'], 'folding', [None]):
            with self.subTest(order=order):
                result = optimize_source('int f(){return 0;}', pass_order=order)
                self.assertEqual(result['status'], 'error')
                self.assertEqual(result['trace'], [])

    def test_iteration_validation_and_limit_diagnostic(self):
        for limit in (0, -1, True, '8', 31):
            with self.subTest(limit=limit):
                self.assertEqual(optimize_source('int f(){return 0;}', max_iterations=limit)['status'], 'error')
        result = optimize_source('int f(){return 1+2;}', pass_order=['folding'], max_iterations=1)
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(any('iteration limit' in item['message'] for item in result['diagnostics']))

    def test_rejects_unsupported_features_explicitly(self):
        sources = [
            'int f(){int *p;return 0;}',
            'int f(){int a[2];return 0;}',
            'int global=1;int f(){return global;}',
            'int f(){volatile int x=1;return x;}',
            'int f(){long x=1;return 0;}',
            'int f(){float x=1.0;return 0;}',
            '#define N 1\nint f(){return N;}',
            'int f(){static int x=1;return x;}',
            'int f(){return sizeof(int);}',
            'int f(){int x=1;return &x;}',
            'int f(int x){switch(x){case 1:return 0;default:return 2;}}',
            'int f(){const int x=1;x=2;return x;}',
        ]
        for source in sources:
            with self.subTest(source=source):
                result = optimize_source(source)
                self.assertEqual(result['status'], 'unsupported', result)
                self.assertTrue(any(item['severity'] == 'error' for item in result['diagnostics']))
                self.assertEqual(result['optimized_code'], source)

    def test_preprocessor_boundaries_and_unknown_call_type(self):
        for source in (
            '#include <assert.h>\nint main(){int x=0;assert(x);return 0;}',
            '#include <string.h>\nint f(){return (1?-1:strlen(""))<0;}',
            'int main(){int x=0;// comment' + chr(92) + chr(10) + 'x=1;\nreturn x;}',
        ):
            with self.subTest(source=source):
                self.assertEqual(optimize_source(source)['status'], 'unsupported')
        source = '#include <stdlib.h>\nint f(){return (1?-1:strtoul("",0,10))<0;}'
        result = optimize_source(source)
        self.assertEqual(result['status'], 'ok', result)
        self.assertIn('strtoul', result['optimized_code'])
        self.assertNotIn('return 1;', result['optimized_code'])

    def test_void_cast_is_preserved(self):
        result = optimize_source('void f(void){(void)1;}')
        self.assertEqual(result['status'], 'ok', result)
        self.assertIn('(void) 1', result['optimized_code'])

    def test_invalid_c_is_a_diagnostic(self):
        result = optimize_source('int f( {')
        self.assertEqual(result['status'], 'error')
        self.assertTrue(result['diagnostics'])

    def test_include_and_comment_handling_preserves_string_contents(self):
        source = '#include <stdio.h>\nint main(){/* comment */printf("https://example.com /* literal */");return 0;}'
        result = optimize_source(source)
        self.assertEqual(result['status'], 'ok', result)
        self.assertIn('#include <stdio.h>', result['optimized_code'])
        self.assertIn('https://example.com /* literal */', result['optimized_code'])
        self.assertTrue(any(item['severity'] == 'warning' for item in result['diagnostics']))

    def test_does_not_fold_undefined_or_implementation_defined_arithmetic(self):
        for expression, retained in [
            ('2147483647+1', '2147483647 + 1'),
            ('1/0', '1 / 0'),
            ('(-2147483647-1)/-1', '/ (-1)'),
            ('1<<32', '1 << 32'),
            ('-5>>1', '>> 1'),
            ('(int)4294967295u', '(int) 4294967295u'),
        ]:
            with self.subTest(expression=expression):
                result = optimize_source('int f(){return ' + expression + ';}', pass_order=['folding'])
                self.assertEqual(result['status'], 'ok', result)
                self.assertIn(retained, result['optimized_code'])

    def test_branch_assignments_reach_successor_read(self):
        result = optimize_source('int f(int b){int x;if(b){x=1;}else{x=2;}return x;}', pass_order=['unused'])
        self.assertEqual(result['status'], 'ok')
        self.assertIn('x = 1;', result['optimized_code'])
        self.assertIn('x = 2;', result['optimized_code'])

    def test_dead_initializer_retains_needed_declaration(self):
        source = 'int read_value();int f(){int x=123;x=read_value();return x;}'
        result = optimize_source(source, pass_order=['unused'])
        self.assertEqual(result['status'], 'ok', result)
        self.assertIn('int x;', result['optimized_code'])
        self.assertIn('x = read_value();', result['optimized_code'])
        self.assertNotIn('123', result['optimized_code'])


@unittest.skipUnless(shutil.which('gcc'), 'GCC is optional; required for differential execution tests')
class CompilerDifferentialTests(unittest.TestCase):
    """Compile only the fixed, inspected fixtures below; never arbitrary input."""
    def compile_run(self, source, directory, name):
        executable = Path(directory) / (name + '.exe')
        compiled = subprocess.run(
            [shutil.which('gcc'), '-std=c11', '-O0', '-x', 'c', '-', '-o', str(executable)],
            input=source, text=True, capture_output=True, timeout=15)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        executed = subprocess.run([str(executable)], capture_output=True, timeout=2)
        return executed.returncode, executed.stdout, executed.stderr

    def equivalent(self, source, order=None):
        result = optimize_source(source, pass_order=order)
        self.assertEqual(result['status'], 'ok', result['diagnostics'])
        temporary_root = Path(__file__).resolve().parents[1] / '.test-work'
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='optilab-regression-', dir=temporary_root) as directory:
            original = self.compile_run(source, directory, 'original')
            optimized = self.compile_run(result['optimized_code'], directory, 'optimized')
        self.assertEqual(optimized, original, result['optimized_code'])
        return result

    def test_known_semantic_regressions(self):
        fixtures = {
            'loop_initial_facts': 'int main(){int x=0;while(x<3){x=x+1;}return x;}',
            'lexical_scope': 'int main(){int x=1;{int x=2;}return x;}',
            'function_scope': 'int f(){int x=7;return x;}int g(int x){return x;}int main(){return g(4);}',
            'negative_remainder': 'int main(){return ((0-5)%3)+10;}',
            'branch_successor': 'int f(int b){int x;if(b){x=1;}else{x=2;}return x;}int main(){return f(0)+f(1);}',
            'list_child_folding': 'int f(int x){return x;}int main(){return f(1+2);}',
        }
        for name, source in fixtures.items():
            with self.subTest(name=name):
                self.equivalent(source)

    def test_mutations_control_flow_and_side_effects(self):
        fixtures = {
            'compound_assignment': 'int main(){int x=1;x+=2;x*=3;x-=1;x/=2;x%=3;return x;}',
            'postincrement_value': 'int main(){int x=1;int y=x++;return y*10+x;}',
            'short_circuit_mutation': 'int main(){int x=1;int y=0&&x++;return x+y;}',
            'for_continue': 'int main(){int sum=0;for(int i=0;i<5;i++){if(i==2)continue;sum+=i;}return sum;}',
            'do_while': 'int main(){int x=0;do{x++;}while(x<3);return x;}',
            'nested_break': 'int main(){int s=0;for(int i=0;i<4;i++){int j=0;while(j<4){j++;if(j==2)break;s+=i;}}return s;}',
            'shadow_in_loop': 'int main(){int x=7;for(int i=0;i<3;i++){int x=i;x+=2;}return x;}',
            'effectful_initializer': '#include <stdio.h>\nint main(){int unused=puts("kept");return 0;}',
            'for_false_init_effect': '#include <stdio.h>\nint main(){for(puts("init");0;puts("step")){puts("body");}return 0;}',
            'branch_call_arg': '#include <stdio.h>\nint f(int b){int x;if(b){x=1;}else{x=2;}printf("%d",x);return x;}int main(){return f(1);}',
            'dead_store_declaration': 'int f(){return 7;}int main(){int x=2;x=f();return x;}',
        }
        for name, source in fixtures.items():
            with self.subTest(name=name):
                self.equivalent(source)

    def test_int32_unsigned32_conversions(self):
        fixtures = {
            'unsigned_wrap': 'int main(){unsigned x=4294967295u;return x+1u;}',
            'negative_unsigned_compare': 'int main(){return (-1<1u)?1:0;}',
            'ternary_common_type': 'int main(){unsigned x=1?-1:0u;return x==4294967295u?0:1;}',
            'int_min_type': 'int f(unsigned u){return (-2147483647-1)<u;}int main(){return f(1u);}',
            'negative_division': 'int main(){return ((0-5)/3)+10;}',
            'signed_shift': 'int main(){return (-5>>1)+10;}',
            'unsigned_bitwise': 'int main(){unsigned x=~0u;x^=1u;return x==4294967294u?0:1;}',
            'compound_usual_conversion': 'int main(){int x=-1;x/=2u;return x==2147483647?0:1;}',
        }
        for name, source in fixtures.items():
            with self.subTest(name=name):
                self.equivalent(source)

    def test_pass_reordering_preserves_results(self):
        source = 'int f(int b){int x=4;if(b){x=1+2;}else{x=7-2;}return x;}int main(){return f(0)+f(1);}'
        for order in (['unused', 'dce', 'folding', 'propagation'], ['folding'], ['propagation', 'unused']):
            with self.subTest(order=order):
                self.equivalent(source, order)


if __name__ == '__main__':
    unittest.main()
