"""Reproducible local compiler experiments using the Python standard library.

This module does not execute user programs on import. ``run_experiment`` compiles
and executes both programs locally; it is a developer tool, not an execution
sandbox. Equality describes observations on the supplied cases, never a proof.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
import uuid

SCHEMA_VERSION = 1
MAX_SOURCE_BYTES = 200_000
MAX_CASES = 16
MAX_REPETITIONS = 10
MAX_CAPTURE_BYTES = 128_000
OPTIMIZATIONS = frozenset(('-O0', '-O1', '-O2', '-O3', '-Os', '-Oz', '-Og'))
_COMPILER_NAME = re.compile(r'^(?:[A-Za-z0-9_.+-]+-)?(?:gcc|clang|cc)(?:-[0-9.]+)?(?:\.exe)?$', re.I)
_WINDOWS_CRASHES = frozenset((0xC0000005, 0xC000001D, 0xC0000094, 0xC00000FD, 0xC0000135, 0xC0000409))


def _capture(stream):
    stream.seek(0)
    digest = hashlib.sha256()
    chunks = []
    total = 0
    while True:
        data = stream.read(64 * 1024)
        if not data:
            break
        digest.update(data)
        if total < MAX_CAPTURE_BYTES:
            chunks.append(data[:MAX_CAPTURE_BYTES - total])
        total += len(data)
    return {
        'text': b''.join(chunks).decode('utf-8', errors='replace'),
        'sha256': digest.hexdigest(),
        'bytes': total,
        'truncated': total > MAX_CAPTURE_BYTES,
    }


def _stop_process(process):
    """Terminate a timed-out process and, where supported, its descendants."""
    if os.name == 'nt':
        try:
            subprocess.run(
                ['taskkill', '/PID', str(process.pid), '/T', '/F'],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=3, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            process.kill()


def _execute(command, *, cwd=None, stdin='', timeout=5.0, env=None):
    """Capture full output hashes but bound text retained in JSON reports."""
    result = {
        'command': [str(part) for part in command], 'returncode': None,
        'stdout': '', 'stderr': '', 'elapsed_seconds': 0.0,
        'timed_out': False, 'error': None,
    }
    began = time.perf_counter()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
        try:
            process = subprocess.Popen(
                result['command'], cwd=cwd, env=env, stdin=subprocess.PIPE,
                stdout=out, stderr=err, shell=False, **options,
            )
            try:
                process.communicate(input=stdin.encode('utf-8'), timeout=timeout)
            except subprocess.TimeoutExpired:
                result['timed_out'] = True
                _stop_process(process)
                try:
                    process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            result['returncode'] = process.returncode
        except (OSError, subprocess.SubprocessError) as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'
        result['elapsed_seconds'] = time.perf_counter() - began
        for name, stream in (('stdout', out), ('stderr', err)):
            captured = _capture(stream)
            result[name] = captured['text']
            for key in ('sha256', 'bytes', 'truncated'):
                result[f'{name}_{key}'] = captured[key]
    return result


def _compiler_environment(path):
    env = os.environ.copy()
    env['PATH'] = str(Path(path).parent) + os.pathsep + env.get('PATH', '')
    return env


def _compiler_info(name, path):
    info = {'name': name, 'path': None, 'available': False, 'version': None, 'target': None, 'kind': name, 'reason': None}
    if not path:
        info['reason'] = 'Compiler was not found.'
        return info
    path = str(Path(path).resolve())
    info['path'] = path
    env = _compiler_environment(path)
    version = _execute([path, '--version'], timeout=5, env=env)
    info['version_command'] = version['command']
    if version['error'] or version['timed_out'] or version['returncode'] != 0:
        info['reason'] = version['error'] or ('Compiler version query timed out.' if version['timed_out'] else version['stderr'] or 'Compiler version query failed.')
        return info
    info['version'] = (version['stdout'] or version['stderr']).strip()
    lower = info['version'].lower()
    if 'clang' in lower:
        info['kind'] = 'clang'
    elif 'gcc' in lower or 'free software foundation' in lower:
        info['kind'] = 'gcc'
    else:
        info['kind'] = 'clang' if 'clang' in Path(path).name.lower() else 'gcc'
    info['available'] = True
    target = _execute([path, '-dumpmachine'], timeout=5, env=env)
    info['target_command'] = target['command']
    if target['returncode'] == 0 and not target['error'] and not target['timed_out']:
        info['target'] = target['stdout'].strip()
    return info


def toolchains():
    """Return Clang/GCC discovery and version information without compiling C."""
    fallbacks = {
        'clang': ('C:/Program Files/LLVM/bin/clang.exe', 'C:/msys64/mingw64/bin/clang.exe', 'C:/msys64/ucrt64/bin/clang.exe'),
        'gcc': ('C:/msys64/mingw64/bin/gcc.exe', 'C:/msys64/ucrt64/bin/gcc.exe'),
    }
    found = []
    for name in ('clang', 'gcc'):
        path = shutil.which(name)
        if path is None and os.name == 'nt':
            path = next((candidate for candidate in fallbacks[name] if Path(candidate).is_file()), None)
        found.append(_compiler_info(name, path))
    if not any(item['available'] for item in found):
        cc = shutil.which('cc')
        if cc:
            found.append(_compiler_info('cc', cc))
    return found


def _choose_compiler(compiler):
    if compiler is None:
        discovered = toolchains()
        return next((item for item in discovered if item['available']), discovered[0])
    try:
        compiler = os.fspath(compiler)
    except TypeError as exc:
        raise ValueError('compiler must be a GCC/Clang executable name or path.') from exc
    if not isinstance(compiler, str) or not _COMPILER_NAME.fullmatch(Path(compiler).name):
        raise ValueError('compiler must name gcc, clang, cc, or a versioned/target-prefixed variant; shell commands are not accepted.')
    path = shutil.which(compiler)
    if path is None and Path(compiler).is_file():
        path = str(Path(compiler).resolve())
    return _compiler_info(Path(compiler).name, path)


def _validate_inputs(original_source, candidate_source, optimization, cases, repetitions, timeout):
    for name, source in (('original_source', original_source), ('candidate_source', candidate_source)):
        if not isinstance(source, str) or not source.strip() or '\x00' in source:
            raise ValueError(f'{name} must be nonempty C source without NUL characters.')
        if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
            raise ValueError(f'{name} exceeds {MAX_SOURCE_BYTES} UTF-8 bytes.')
    if not isinstance(optimization, str) or optimization not in OPTIMIZATIONS:
        raise ValueError('optimization must be one of ' + ', '.join(sorted(OPTIMIZATIONS)) + '.')
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or not 1 <= repetitions <= MAX_REPETITIONS:
        raise ValueError(f'repetitions must be an integer from 1 to {MAX_REPETITIONS}.')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0.05 <= timeout <= 30 or not math.isfinite(timeout):
        raise ValueError('timeout must be a finite number from 0.05 to 30 seconds.')
    cases = [{'label': 'default', 'stdin': '', 'args': []}] if cases is None else cases
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError(f'cases must be a list containing 1 to {MAX_CASES} cases.')
    normalized = []
    for index, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            raise ValueError('Each case must be an object with label, stdin, and args fields.')
        label = case.get('label', f'case-{index}')
        stdin = case.get('stdin', '')
        args = case.get('args', [])
        if not isinstance(label, str) or not label.strip() or len(label) > 120:
            raise ValueError('Case labels must be nonempty strings of at most 120 characters.')
        if not isinstance(stdin, str) or '\x00' in stdin or len(stdin.encode('utf-8')) > 1_000_000:
            raise ValueError('Case stdin must be text without NUL, at most 1,000,000 UTF-8 bytes.')
        if not isinstance(args, list) or len(args) > 32 or any(not isinstance(arg, str) or '\x00' in arg or len(arg) > 4096 for arg in args):
            raise ValueError('Case args must be a list of at most 32 strings, each at most 4096 characters without NUL.')
        normalized.append({'label': label, 'stdin': stdin, 'args': list(args)})
    return normalized


def _succeeded(execution):
    return execution['returncode'] == 0 and not execution['timed_out'] and not execution['error']


def _build(name, source, directory, compiler, optimization, compile_timeout):
    source_path = directory / f'{name}.c'
    executable = directory / (f'{name}.exe' if os.name == 'nt' else name)
    assembly = directory / f'{name}.s'
    remarks = directory / f'{name}.opt.txt'
    llvm_ir = directory / f'{name}.ll'
    source_path.write_text(source, encoding='utf-8', newline='\n')
    flags = [optimization, '-std=c11', '-Wall', '-Wextra', '-g']
    diagnostic_flags = [f'-fopt-info-all={remarks}'] if compiler['kind'] == 'gcc' else ['-Rpass=.*', '-Rpass-missed=.*', '-Rpass-analysis=.*']
    prefix = [compiler['path'], *flags]
    env = _compiler_environment(compiler['path'])
    compile_result = _execute([*prefix, *diagnostic_flags, str(source_path), '-o', str(executable)], cwd=str(directory), timeout=compile_timeout, env=env)
    if compiler['kind'] == 'clang':
        remarks.write_text(compile_result['stderr'], encoding='utf-8')
    build = {
        'success': _succeeded(compile_result) and executable.is_file(),
        'flags': flags, 'compile': compile_result, 'assembly': None, 'llvm_ir': None,
        'artifacts': {'source': str(source_path), 'executable': str(executable) if executable.is_file() else None, 'assembly': None, 'optimization_remarks': str(remarks) if remarks.is_file() else None, 'llvm_ir': None},
    }
    if not build['success']:
        return build
    build['assembly'] = _execute([*prefix, '-S', str(source_path), '-o', str(assembly)], cwd=str(directory), timeout=compile_timeout, env=env)
    if _succeeded(build['assembly']) and assembly.is_file():
        build['artifacts']['assembly'] = str(assembly)
    if compiler['kind'] == 'clang':
        build['llvm_ir'] = _execute([*prefix, '-S', '-emit-llvm', str(source_path), '-o', str(llvm_ir)], cwd=str(directory), timeout=compile_timeout, env=env)
        if _succeeded(build['llvm_ir']) and llvm_ir.is_file():
            build['artifacts']['llvm_ir'] = str(llvm_ir)
    return build


def _signature(execution):
    return (execution['returncode'], execution['stdout_sha256'], execution['stderr_sha256'])


def _abnormal(execution):
    code = execution['returncode']
    return execution['timed_out'] or execution['error'] is not None or code is None or code < 0 or (os.name == 'nt' and code in _WINDOWS_CRASHES)


def _compare_case(case):
    executions = case['original'] + case['candidate']
    abnormal = any(_abnormal(execution) for execution in executions)
    unstable = any(len({_signature(execution) for execution in case[name]}) > 1 for name in ('original', 'candidate'))
    differences = []
    if not abnormal and not unstable:
        original, candidate = case['original'][0], case['candidate'][0]
        for field in ('returncode', 'stdout', 'stderr'):
            key = field if field == 'returncode' else field + '_sha256'
            if original[key] != candidate[key]:
                differences.append(field)
    case['comparison'] = {'equal': None if abnormal or unstable else not differences, 'fields_differing': differences, 'nondeterministic_observations': unstable, 'abnormal_execution': abnormal}
    case['status'] = 'inconclusive' if abnormal or unstable else ('counterexample' if differences else 'tested_equal')
    return case


def _measurement(executions):
    samples = [execution['elapsed_seconds'] for execution in executions if not _abnormal(execution)]
    return {'samples': samples, 'sample_count': len(samples), 'median_seconds': statistics.median(samples) if samples else None, 'min_seconds': min(samples) if samples else None, 'max_seconds': max(samples) if samples else None}


def _finish(report):
    summaries = {
        'tested_equal': 'Both programs produced matching stdout, stderr, and exit codes on the supplied cases and repetitions. This is observed agreement, not a proof of equivalence.',
        'counterexample': 'At least one supplied case produced a repeatable difference in stdout, stderr, or exit code.',
        'inconclusive': 'A timeout, abnormal execution, launch failure, or changing observations prevented a reliable comparison.',
        'compile_error': 'At least one program did not compile and link successfully. Inspect the recorded compiler diagnostics.',
        'unavailable': 'No usable requested GCC/Clang compiler was found.',
    }
    report['summary'] = summaries[report['status']]
    Path(report['artifacts']['report']).write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    return report


def run_experiment(original_source, candidate_source, *, compiler=None, optimization='-O2', cases=None, repetitions=3, timeout=2.0, artifact_root=None):
    """Compile two C programs, compare selected executions, and save evidence.

    Invalid settings raise ``ValueError`` before C compilation/execution. Other
    outcomes return a JSON-safe report with status ``tested_equal``,
    ``counterexample``, ``inconclusive``, ``compile_error``, or ``unavailable``.
    ``timeout`` applies per program execution; compilation commands receive a
    separate bounded timeout recorded in configuration. Runtime samples include
    process startup, I/O, scheduling, and this runner's waiting overhead.
    """
    cases = _validate_inputs(original_source, candidate_source, optimization, cases, repetitions, timeout)
    selected = _choose_compiler(compiler)
    root = (Path(artifact_root) if artifact_root is not None else Path.cwd() / '.optilab' / 'runs').resolve()
    run_id = uuid.uuid4().hex
    directory = root / run_id
    directory.mkdir(parents=True, exist_ok=False)
    compile_timeout = max(5.0, min(60.0, float(timeout) * 5.0))
    report = {
        'schema_version': SCHEMA_VERSION, 'run_id': run_id, 'status': 'unavailable', 'compiler': selected,
        'configuration': {'optimization': optimization, 'repetitions': repetitions, 'timeout': float(timeout), 'compile_timeout': compile_timeout, 'cases': cases},
        'environment': {'platform': platform.platform(), 'architecture': platform.machine(), 'python_version': platform.python_version()},
        'sources': {}, 'builds': {}, 'cases': [],
        'measurements': {'metric': 'process_wall_seconds', 'includes_process_startup': True, 'includes_runner_waiting_overhead': True, 'by_case': [], 'warning': 'Small process timings are dominated by startup, I/O, scheduling, and measurement overhead. These observations are not kernel-only benchmark results or proof of a speedup.'},
        'artifacts': {'directory': str(directory), 'report': str(directory / 'report.json')},
        'limitations': [
            'Only supplied inputs and observed stdout, stderr, and exit codes are compared. Memory, filesystem, network, and other side effects are not compared.',
            'Matching observations do not prove equivalence or absence of C undefined behavior. No sanitizer or formal verifier is run.',
            'Programs execute locally with the runner account permissions. This runner is not a security sandbox.',
            'Compiler diagnostics and generated assembly are evidence of this exact compiler configuration, not a complete causal explanation.',
            'Text output is decoded as UTF-8 with replacement and truncated after 128,000 bytes; comparisons use full raw-output SHA-256 hashes.',
            'Known abnormal exits, timeouts, and changing observations are classified as inconclusive.',
        ],
    }
    for name, source in (('original', original_source), ('candidate', candidate_source)):
        path = directory / f'{name}.c'
        path.write_text(source, encoding='utf-8', newline='\n')
        encoded = source.encode('utf-8')
        report['sources'][name] = {'sha256': hashlib.sha256(encoded).hexdigest(), 'bytes': len(encoded), 'path': str(path)}
        report['artifacts'][f'{name}_source'] = str(path)
    if not selected['available']:
        return _finish(report)
    for name, source in (('original', original_source), ('candidate', candidate_source)):
        report['builds'][name] = _build(name, source, directory, selected, optimization, compile_timeout)
    if not all(build['success'] for build in report['builds'].values()):
        report['status'] = 'compile_error'
        return _finish(report)
    env = _compiler_environment(selected['path'])
    for specification in cases:
        case = {**specification, 'original': [], 'candidate': []}
        for repetition in range(repetitions):
            order = ('original', 'candidate') if repetition % 2 == 0 else ('candidate', 'original')
            for name in order:
                execution = _execute([report['builds'][name]['artifacts']['executable'], *specification['args']], cwd=str(directory), stdin=specification['stdin'], timeout=float(timeout), env=env)
                execution['repetition'] = repetition + 1
                case[name].append(execution)
            if any(_abnormal(case[name][-1]) for name in order):
                break
        _compare_case(case)
        report['cases'].append(case)
        original = _measurement(case['original'])
        candidate = _measurement(case['candidate'])
        ratio = None
        if case['status'] == 'tested_equal' and original['median_seconds'] and candidate['median_seconds']:
            ratio = original['median_seconds'] / candidate['median_seconds']
        report['measurements']['by_case'].append({'label': specification['label'], 'original': original, 'candidate': candidate, 'median_ratio_original_over_candidate': ratio})
    statuses = {case['status'] for case in report['cases']}
    report['status'] = 'counterexample' if 'counterexample' in statuses else ('inconclusive' if 'inconclusive' in statuses else 'tested_equal')
    return _finish(report)
