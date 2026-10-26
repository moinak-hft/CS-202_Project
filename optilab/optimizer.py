"""Conservative, inspectable optimizer for a documented scalar C subset.

No code is executed or compiled here. Signed arithmetic models 32-bit int;
unsigned arithmetic models 32-bit unsigned int. Unsupported constructs receive
explicit diagnostics rather than speculative transformations.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import time
from pycparser import c_ast, c_generator, c_parser

PASS_NAMES = ('propagation', 'folding', 'dce', 'unused')
_KNOWN_INT_CALLS = {'printf', 'puts', 'putchar', 'getchar', 'abs', 'rand', 'atoi'}
INT_MIN, INT_MAX, UINT_MAX = -(1 << 31), (1 << 31) - 1, (1 << 32) - 1


def _code(node):
    return c_generator.CGenerator().visit(node) if node is not None else ''


def _line(node):
    return node.coord.line if node is not None and node.coord else None


def _walk(node):
    if node is not None:
        yield node
        for _, child in node.children():
            yield from _walk(child)


def _set_child(parent, name, value):
    if '[' in name:
        field, index = name.rstrip(']').split('[')
        getattr(parent, field)[int(index)] = value
    else:
        setattr(parent, name, value)


def _event(events, node, before, after, reason):
    if before != after:
        events.append(dict(line=_line(node), before=before, after=after, reason=reason))


@dataclass(frozen=True)
class _Value:
    value: int
    unsigned: bool = False


@dataclass(frozen=True)
class _Symbol:
    key: int
    name: str
    unsigned: bool
    const: bool = False


def _literal(node):
    if not isinstance(node, c_ast.Constant) or node.type == 'string':
        return None
    spelling = node.value
    match = re.fullmatch(r'(0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*)([uU]?)', spelling)
    if not match:
        return None
    digits, suffix = match.groups()
    base = 16 if digits.lower().startswith('0x') else (8 if len(digits) > 1 and digits.startswith('0') else 10)
    value = int(digits, base)
    unsigned = bool(suffix) or (base != 10 and value > INT_MAX)
    if value > (UINT_MAX if unsigned else INT_MAX):
        return None
    return _Value(value, unsigned)


def _convert(value, unsigned):
    if value is None:
        return None
    if unsigned:
        return _Value(value.value & UINT_MAX, True)
    if INT_MIN <= value.value <= INT_MAX:
        return _Value(value.value, False)
    # Conversion of an out-of-range unsigned integer to int is implementation-defined.
    return None


def _constant(value, coord=None):
    if value.unsigned:
        return c_ast.Constant('unsigned int', str(value.value) + 'u', coord=coord)
    if value.value >= 0:
        return c_ast.Constant('int', str(value.value), coord=coord)
    if value.value == INT_MIN:
        # A bare -2147483648 has a wider literal type in C; preserve int expression type.
        return c_ast.BinaryOp('-', c_ast.UnaryOp('-', c_ast.Constant('int', str(INT_MAX), coord=coord), coord=coord), c_ast.Constant('int', '1', coord=coord), coord=coord)
    return c_ast.UnaryOp('-', c_ast.Constant('int', str(-value.value), coord=coord), coord=coord)


def _binary(op, left, right):
    if left is None or right is None:
        return None
    unsigned = left.unsigned or right.unsigned
    a = left.value & UINT_MAX if unsigned else left.value
    b = right.value & UINT_MAX if unsigned else right.value
    if op in ('<', '<=', '>', '>=', '==', '!='):
        comparison = {'<': a < b, '<=': a <= b, '>': a > b, '>=': a >= b, '==': a == b, '!=': a != b}[op]
        return _Value(int(comparison))
    if op in ('<<', '>>'):
        # Shift result type is the promoted left type, not the usual binary type.
        a, b, unsigned = left.value, right.value, left.unsigned
        if not 0 <= b < 32:
            return None
        if op == '>>':
            if a < 0:
                return None  # Negative signed right shift is implementation-defined in C11.
            return _Value(a >> b, unsigned)
        if not unsigned and a < 0:
            return None
        value = a << b
    elif op == '+':
        value = a + b
    elif op == '-':
        value = a - b
    elif op == '*':
        value = a * b
    elif op in ('/', '%'):
        if b == 0 or (not unsigned and a == INT_MIN and b == -1):
            return None
        quotient = abs(a) // abs(b)
        if (a < 0) != (b < 0):
            quotient = -quotient
        value = quotient if op == '/' else a - quotient * b
    elif op == '&':
        value = a & b
    elif op == '|':
        value = a | b
    elif op == '^':
        value = a ^ b
    else:
        return None
    if unsigned:
        return _Value(value & UINT_MAX, True)
    return _Value(value) if INT_MIN <= value <= INT_MAX else None


def _is_void_type(type_node):
    while isinstance(type_node, (c_ast.Decl, c_ast.Typename)):
        type_node = type_node.type
    return isinstance(type_node, c_ast.TypeDecl) and isinstance(type_node.type, c_ast.IdentifierType) and type_node.type.names == ['void']


def _type_unsigned(type_node):
    while isinstance(type_node, (c_ast.Decl, c_ast.Typename)):
        type_node = type_node.type
    if isinstance(type_node, c_ast.TypeDecl) and isinstance(type_node.type, c_ast.IdentifierType):
        return 'unsigned' in type_node.type.names
    return False


class _Bindings:
    """Lexical declaration identities, rebuilt after every transformation pass."""
    def __init__(self, tree):
        self.nodes = {}
        self.symbols = {}
        self.scopes = []
        self.diagnostics = []
        self.return_types = {}
        self.loop_depth = 0
        for ext in tree.ext:
            if isinstance(ext, c_ast.FuncDef):
                self.return_types[ext.decl.name] = _type_unsigned(ext.decl.type.type)
            elif isinstance(ext, c_ast.Decl) and isinstance(ext.type, c_ast.FuncDecl):
                self.return_types[ext.name] = _type_unsigned(ext.type.type)
        for ext in tree.ext:
            if isinstance(ext, c_ast.FuncDef):
                self.scopes = [{}]
                if ext.decl.type.args:
                    for param in ext.decl.type.args.params:
                        if isinstance(param, c_ast.Decl):
                            self._declare(param)
                self._visit(ext.body, root_block=True)
            elif not (isinstance(ext, c_ast.Decl) and isinstance(ext.type, c_ast.FuncDecl)):
                self._diagnose(ext, 'Global data declarations are outside the supported scalar-local subset.')

    def _diagnose(self, node, message):
        if len(self.diagnostics) < 30:
            self.diagnostics.append(dict(severity='error', message=message, line=_line(node)))

    def _declare(self, node):
        if not node.name:
            return
        if node.name in self.scopes[-1]:
            self._diagnose(node, 'Duplicate declaration in one scope: ' + node.name)
        symbol = _Symbol(len(self.symbols), node.name, _type_unsigned(node), 'const' in node.quals)
        self.symbols[symbol.key] = symbol
        self.scopes[-1][node.name] = symbol
        self.nodes[id(node)] = symbol

    def _lookup(self, node):
        for scope in reversed(self.scopes):
            if node.name in scope:
                self.nodes[id(node)] = scope[node.name]
                return
        self._diagnose(node, 'Unknown scalar identifier: ' + node.name)

    def _visit(self, node, root_block=False):
        if node is None:
            return
        if isinstance(node, c_ast.Compound):
            if not root_block:
                self.scopes.append({})
            for statement in node.block_items or []:
                self._visit(statement)
            if not root_block:
                self.scopes.pop()
        elif isinstance(node, c_ast.Decl):
            if isinstance(node.type, c_ast.FuncDecl):
                self._diagnose(node, 'Local function declarations are unsupported; place prototypes at file scope.')
                return
            self._declare(node)
            self._visit(node.init)
        elif isinstance(node, c_ast.ID):
            self._lookup(node)
        elif isinstance(node, c_ast.FuncCall):
            if not isinstance(node.name, c_ast.ID):
                self._diagnose(node, 'Only direct function calls are supported.')
            elif any(node.name.name in scope for scope in self.scopes):
                self._diagnose(node.name, 'Calling a local scalar as a function is unsupported.')
            self._visit(node.args)
        elif isinstance(node, c_ast.For):
            self.scopes.append({})
            self._visit(node.init)
            self.loop_depth += 1
            self._visit(node.cond)
            self._visit(node.stmt)
            self._visit(node.next)
            self.loop_depth -= 1
            self.scopes.pop()
        elif isinstance(node, (c_ast.While, c_ast.DoWhile)):
            self.loop_depth += 1
            self._visit(node.cond)
            self._visit(node.stmt)
            self.loop_depth -= 1
        elif isinstance(node, (c_ast.Break, c_ast.Continue)):
            if not self.loop_depth:
                self._diagnose(node, 'break/continue requires an enclosing loop.')
        else:
            for _, child in node.children():
                self._visit(child)

    def symbol(self, node):
        return self.nodes.get(id(node))


def _expr_unsigned(node, bindings):
    if isinstance(node, c_ast.ID):
        symbol = bindings.symbol(node)
        return symbol.unsigned if symbol else False
    if isinstance(node, c_ast.Constant):
        value = _literal(node)
        return value.unsigned if value else False
    if isinstance(node, c_ast.BinaryOp):
        if node.op in ('&&', '||', '<', '<=', '>', '>=', '==', '!='):
            return False
        if node.op in ('<<', '>>'):
            return _expr_unsigned(node.left, bindings)
        left, right = _expr_unsigned(node.left, bindings), _expr_unsigned(node.right, bindings)
        return None if left is None or right is None else left or right
    if isinstance(node, c_ast.UnaryOp):
        return False if node.op == '!' else _expr_unsigned(node.expr, bindings)
    if isinstance(node, c_ast.Cast):
        return None if _is_void_type(node.to_type) else _type_unsigned(node.to_type)
    if isinstance(node, c_ast.TernaryOp):
        left, right = _expr_unsigned(node.iftrue, bindings), _expr_unsigned(node.iffalse, bindings)
        return None if left is None or right is None else left or right
    if isinstance(node, c_ast.FuncCall) and isinstance(node.name, c_ast.ID):
        return bindings.return_types.get(node.name.name, False if node.name.name in _KNOWN_INT_CALLS else None)
    if isinstance(node, c_ast.Assignment):
        return _expr_unsigned(node.lvalue, bindings)
    if isinstance(node, c_ast.ExprList) and node.exprs:
        return _expr_unsigned(node.exprs[-1], bindings)
    return False


def _evaluate(node, bindings):
    if node is None:
        return None
    if isinstance(node, c_ast.Constant):
        return _literal(node)
    if isinstance(node, c_ast.BinaryOp):
        left = _evaluate(node.left, bindings)
        if left is None:
            return None
        if node.op == '&&' and not left.value:
            return _Value(0)
        if node.op == '||' and left.value:
            return _Value(1)
        right = _evaluate(node.right, bindings)
        if right is None:
            return None
        if node.op in ('&&', '||'):
            return _Value(int(bool(right.value)))
        return _binary(node.op, left, right)
    if isinstance(node, c_ast.UnaryOp):
        value = _evaluate(node.expr, bindings)
        if value is None:
            return None
        if node.op == '!':
            return _Value(int(not value.value))
        if node.op == '+':
            return value
        if node.op == '-':
            if value.unsigned:
                return _Value((-value.value) & UINT_MAX, True)
            return _Value(-value.value) if value.value != INT_MIN else None
        if node.op == '~':
            return _Value((~value.value) & UINT_MAX, True) if value.unsigned else _Value(~value.value)
        return None
    if isinstance(node, c_ast.Cast):
        return None if _is_void_type(node.to_type) else _convert(_evaluate(node.expr, bindings), _type_unsigned(node.to_type))
    if isinstance(node, c_ast.TernaryOp):
        condition = _evaluate(node.cond, bindings)
        if condition is None:
            return None
        chosen = node.iftrue if condition.value else node.iffalse
        result_type = _expr_unsigned(node, bindings)
        return None if result_type is None else _convert(_evaluate(chosen, bindings), result_type)
    return None


def _written(node, bindings):
    keys = set()
    for item in _walk(node):
        target = item.lvalue if isinstance(item, c_ast.Assignment) else (item.expr if isinstance(item, c_ast.UnaryOp) and item.op in ('p++', 'p--', '++', '--') else None)
        symbol = bindings.symbol(target)
        if symbol:
            keys.add(symbol.key)
    return keys


def _references(node, bindings):
    return {bindings.symbol(item).key for item in _walk(node) if isinstance(item, c_ast.ID) and bindings.symbol(item)}


def _effects(node):
    return any(isinstance(item, (c_ast.FuncCall, c_ast.Assignment)) or (isinstance(item, c_ast.UnaryOp) and item.op in ('p++', 'p--', '++', '--')) for item in _walk(node))


def _propagation(tree, bindings, events):
    def expression(node, environment, protected=False):
        if node is None:
            return None
        if isinstance(node, c_ast.ID):
            symbol = bindings.symbol(node)
            if not protected and symbol and symbol.key in environment:
                replacement = _constant(environment[symbol.key], node.coord)
                _event(events, node, _code(node), _code(replacement), 'Replace a read with the known value of its lexical declaration.')
                return replacement
            return node
        if isinstance(node, c_ast.FuncCall):
            if node.args:
                node.args = expression(node.args, environment)
            return node
        if isinstance(node, c_ast.Assignment):
            node.rvalue = expression(node.rvalue, environment)
            return node
        if isinstance(node, c_ast.UnaryOp) and node.op in ('p++', 'p--', '++', '--'):
            return node
        for name, child in list(node.children()):
            _set_child(node, name, expression(child, environment, protected))
        return node

    def prepare_expression(node, environment):
        for key in _written(node, bindings):
            environment.pop(key, None)
        return expression(node, environment)

    def visit(node, environment):
        if node is None:
            return environment
        if isinstance(node, c_ast.Compound):
            for statement in node.block_items or []:
                visit(statement, environment)
        elif isinstance(node, c_ast.Decl):
            symbol = bindings.symbol(node)
            if symbol:
                environment.pop(symbol.key, None)
                node.init = prepare_expression(node.init, environment)
                value = _convert(_evaluate(node.init, bindings), symbol.unsigned)
                if value is not None:
                    environment[symbol.key] = value
        elif isinstance(node, c_ast.DeclList):
            for declaration in node.decls:
                visit(declaration, environment)
        elif isinstance(node, c_ast.Assignment):
            symbol = bindings.symbol(node.lvalue)
            previous = environment.get(symbol.key) if symbol else None
            node.rvalue = prepare_expression(node.rvalue, environment)
            value = _evaluate(node.rvalue, bindings)
            if node.op != '=':
                value = _binary(node.op[:-1], previous, value)
            if symbol:
                environment.pop(symbol.key, None)
                value = _convert(value, symbol.unsigned)
                if value is not None:
                    environment[symbol.key] = value
        elif isinstance(node, c_ast.If):
            node.cond = prepare_expression(node.cond, environment)
            condition = _evaluate(node.cond, bindings)
            incoming = dict(environment)
            then_environment, else_environment = dict(incoming), dict(incoming)
            visit(node.iftrue, then_environment)
            visit(node.iffalse, else_environment)
            if condition is not None:
                merged = then_environment if condition.value else else_environment
            else:
                merged = {key: value for key, value in then_environment.items() if else_environment.get(key) == value}
            environment.clear()
            environment.update(merged)
        elif isinstance(node, (c_ast.While, c_ast.For, c_ast.DoWhile)):
            if isinstance(node, c_ast.For):
                visit(node.init, environment)
            modified = _written(node.stmt, bindings) | _written(node.cond, bindings)
            if isinstance(node, c_ast.For):
                modified |= _written(node.next, bindings)
            for key in modified:
                environment.pop(key, None)
            invariants = dict(environment)
            node.cond = prepare_expression(node.cond, dict(invariants))
            visit(node.stmt, dict(invariants))
            if isinstance(node, c_ast.For):
                node.next = prepare_expression(node.next, dict(invariants))
            # No body facts escape: zero iterations, breaks and continues are possible.
            environment.clear()
            environment.update(invariants)
        elif isinstance(node, c_ast.Return):
            node.expr = prepare_expression(node.expr, environment)
        elif isinstance(node, (c_ast.FuncCall, c_ast.UnaryOp, c_ast.ExprList, c_ast.BinaryOp, c_ast.Cast, c_ast.TernaryOp)):
            prepare_expression(node, environment)
        return environment

    for ext in tree.ext:
        if isinstance(ext, c_ast.FuncDef):
            visit(ext.body, {})  # A new environment for every function.


def _folding(tree, bindings, events):
    def fold(node):
        for name, child in list(node.children()):
            _set_child(node, name, fold(child))
        if isinstance(node, (c_ast.BinaryOp, c_ast.UnaryOp, c_ast.Cast, c_ast.TernaryOp)):
            value = _evaluate(node, bindings)
            if value is not None:
                replacement = _constant(value, node.coord)
                _event(events, node, _code(node), _code(replacement), 'Evaluate a defined int32/unsigned32 expression using C arithmetic and short circuit rules.')
                return replacement
        return node
    fold(tree)


def _terminates(node):
    if isinstance(node, (c_ast.Return, c_ast.Break, c_ast.Continue)):
        return True
    if isinstance(node, c_ast.Compound):
        return any(_terminates(statement) for statement in node.block_items or [])
    if isinstance(node, c_ast.If):
        return node.iffalse is not None and _terminates(node.iftrue) and _terminates(node.iffalse)
    return False


def _dce(tree, bindings, events):
    def transform(node):
        if node is None:
            return None
        if isinstance(node, c_ast.Compound):
            kept = []
            terminated = False
            for statement in node.block_items or []:
                if terminated:
                    _event(events, statement, _code(statement), '', 'Remove a statement after an unconditional control transfer.')
                    continue
                replacement = transform(statement)
                if replacement is not None:
                    kept.append(replacement)
                    terminated = _terminates(replacement)
            node.block_items = kept
        elif isinstance(node, c_ast.If):
            condition = _evaluate(node.cond, bindings)
            if condition is not None:
                selected = node.iftrue if condition.value else node.iffalse
                before = _code(node)
                selected = transform(selected)
                _event(events, node, before, _code(selected), 'Select the only reachable branch of a constant condition; retain its scope.')
                return selected
            node.iftrue = transform(node.iftrue) or c_ast.EmptyStatement(coord=node.coord)
            if node.iffalse:
                node.iffalse = transform(node.iffalse) or c_ast.EmptyStatement(coord=node.coord)
        elif isinstance(node, c_ast.While):
            condition = _evaluate(node.cond, bindings)
            if condition is not None and not condition.value:
                _event(events, node, _code(node), '', 'A side-effect-free false condition makes the loop unreachable.')
                return None
            node.stmt = transform(node.stmt) or c_ast.EmptyStatement(coord=node.coord)
        elif isinstance(node, c_ast.For):
            condition = _evaluate(node.cond, bindings)
            if condition is not None and not condition.value:
                before = _code(node)
                initial = list(node.init.decls) if isinstance(node.init, c_ast.DeclList) else ([node.init] if node.init is not None else [])
                replacement = c_ast.Compound(initial, coord=node.coord) if initial else None
                _event(events, node, before, _code(replacement), 'Remove a never-entered for loop while preserving its initializer and scope.')
                return replacement
            node.stmt = transform(node.stmt) or c_ast.EmptyStatement(coord=node.coord)
        elif isinstance(node, c_ast.DoWhile):
            node.stmt = transform(node.stmt) or c_ast.EmptyStatement(coord=node.coord)
        return node
    for ext in tree.ext:
        if isinstance(ext, c_ast.FuncDef):
            transform(ext.body)


def _unused(tree, bindings, events):
    def backward(node, live_after):
        if node is None:
            return None, set(live_after)
        live = set(live_after)
        if isinstance(node, c_ast.Compound):
            kept = []
            for statement in reversed(node.block_items or []):
                replacement, live = backward(statement, live)
                if replacement is not None:
                    kept.append(replacement)
            node.block_items = list(reversed(kept))
        elif isinstance(node, c_ast.Assignment):
            symbol = bindings.symbol(node.lvalue)
            if symbol:
                if symbol.key not in live and not _effects(node.rvalue):
                    _event(events, node, _code(node), '', 'Remove a local assignment whose value cannot reach a later read.')
                    return None, live
                live.discard(symbol.key)
                live |= _references(node.rvalue, bindings)
                if node.op != '=':
                    live.add(symbol.key)
        elif isinstance(node, c_ast.Decl):
            symbol = bindings.symbol(node)
            if symbol:
                if node.init is not None and symbol.key not in live and not _effects(node.init):
                    before = _code(node)
                    node.init = None
                    _event(events, node, before, _code(node), 'Discard an unread initializer; retain the declaration until remaining uses are checked.')
                else:
                    live |= _references(node.init, bindings)
                live.discard(symbol.key)
        elif isinstance(node, c_ast.Return):
            live = _references(node.expr, bindings)
        elif isinstance(node, c_ast.If):
            node.iftrue, then_live = backward(node.iftrue, live)
            node.iftrue = node.iftrue or c_ast.EmptyStatement(coord=node.coord)
            node.iffalse, else_live = backward(node.iffalse, live)
            live = then_live | else_live | _references(node.cond, bindings)
        elif isinstance(node, (c_ast.While, c_ast.For, c_ast.DoWhile)):
            # Conservative loop boundary: do not delete its body or loop-carried values.
            live |= _references(node, bindings)
        else:
            live |= _references(node, bindings)
        return node, live

    def prune(node, referenced):
        if isinstance(node, c_ast.Compound):
            kept = []
            for statement in node.block_items or []:
                if isinstance(statement, c_ast.Decl):
                    symbol = bindings.symbol(statement)
                    if symbol and symbol.key not in referenced and not _effects(statement.init):
                        _event(events, statement, _code(statement), '', 'Remove a declaration with no remaining references or observable initializer.')
                        continue
                prune(statement, referenced)
                kept.append(statement)
            node.block_items = kept
        elif node is not None:
            for _, child in node.children():
                prune(child, referenced)

    for ext in tree.ext:
        if isinstance(ext, c_ast.FuncDef):
            backward(ext.body, set())
            prune(ext.body, _references(ext.body, bindings))

_ALLOWED_NODES = {
    'FileAST', 'FuncDef', 'Decl', 'DeclList', 'FuncDecl', 'ParamList',
    'TypeDecl', 'IdentifierType', 'Typename', 'Compound', 'Assignment', 'ID',
    'Constant', 'BinaryOp', 'UnaryOp', 'If', 'While', 'For', 'DoWhile',
    'Return', 'Break', 'Continue', 'FuncCall', 'ExprList', 'EmptyStatement',
    'TernaryOp', 'Cast', 'EllipsisParam',
}
_ALLOWED_TYPES = {
    ('int',), ('signed',), ('signed', 'int'), ('int', 'signed'),
    ('unsigned',), ('unsigned', 'int'), ('int', 'unsigned'), ('void',),
}
_BINARY_OPS = {'+', '-', '*', '/', '%', '<', '<=', '>', '>=', '==', '!=',
               '&&', '||', '&', '|', '^', '<<', '>>'}
_UNARY_OPS = {'+', '-', '~', '!', 'p++', 'p--', '++', '--'}
_ASSIGNMENT_OPS = {'=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='}


def _validate(tree, bindings):
    diagnostics = list(bindings.diagnostics)
    call_arguments = {id(node.args) for node in _walk(tree) if isinstance(node, c_ast.FuncCall) and node.args}

    def diagnose(node, message):
        if len(diagnostics) < 30:
            diagnostics.append(dict(severity='error', message=message, line=_line(node)))

    def inspect(node, parent=None):
        kind = type(node).__name__
        if kind not in _ALLOWED_NODES:
            diagnose(node, 'Unsupported C construct: ' + kind + '. Use scalar int/unsigned int locals and structured control flow.')
            return
        if isinstance(node, c_ast.IdentifierType) and tuple(node.names) not in _ALLOWED_TYPES:
            diagnose(node, 'Only 32-bit int, unsigned int, and void function returns are supported; found ' + ' '.join(node.names) + '.')
        if isinstance(node, c_ast.TypeDecl):
            if any(qualifier not in ('const',) for qualifier in node.quals):
                diagnose(node, 'volatile, restrict, and atomic-qualified objects are unsupported.')
            if isinstance(node.type, c_ast.IdentifierType) and node.type.names == ['void']:
                # void is permitted in function returns and unnamed (void) parameters.
                if not isinstance(parent, (c_ast.FuncDecl, c_ast.Typename)):
                    diagnose(node, 'void objects are unsupported.')
        if isinstance(node, c_ast.Decl):
            if node.bitsize is not None or node.align:
                diagnose(node, 'Bit fields and explicit object alignment are unsupported.')
            if not isinstance(node.type, c_ast.FuncDecl) and any(storage not in ('auto', 'register') for storage in node.storage):
                diagnose(node, 'Static, external, and thread-local data are unsupported.')
            if any(qualifier not in ('const',) for qualifier in node.quals):
                diagnose(node, 'volatile, restrict, and atomic-qualified objects are unsupported.')
        if isinstance(node, c_ast.Constant):
            if node.type == 'string':
                if not isinstance(parent, c_ast.ExprList) or id(parent) not in call_arguments:
                    diagnose(node, 'String literals are supported only as direct function-call arguments.')
            elif _literal(node) is None:
                diagnose(node, 'Only int32/unsigned32 integer literals are supported; found ' + node.value + '.')
        if isinstance(node, c_ast.BinaryOp) and node.op not in _BINARY_OPS:
            diagnose(node, 'Unsupported binary operator: ' + node.op)
        if isinstance(node, c_ast.UnaryOp):
            if node.op not in _UNARY_OPS:
                diagnose(node, 'Unsupported unary operator ' + node.op + '; address-taking, dereferencing, and sizeof are outside this subset.')
            if node.op in ('p++', 'p--', '++', '--') and not isinstance(node.expr, c_ast.ID):
                diagnose(node, 'Increment/decrement requires a scalar local identifier.')
            symbol = bindings.symbol(node.expr)
            if node.op in ('p++', 'p--', '++', '--') and symbol and symbol.const:
                diagnose(node, 'Cannot modify a const-qualified local: ' + symbol.name)
        if isinstance(node, c_ast.Assignment):
            if node.op not in _ASSIGNMENT_OPS or not isinstance(node.lvalue, c_ast.ID):
                diagnose(node, 'Only assignments to scalar local identifiers are supported.')
            symbol = bindings.symbol(node.lvalue)
            if symbol and symbol.const:
                diagnose(node, 'Cannot assign a const-qualified local: ' + symbol.name)
        for _, child in node.children():
            inspect(child, node)

    inspect(tree)
    if not any(isinstance(ext, c_ast.FuncDef) for ext in tree.ext):
        diagnostics.append(dict(severity='error', message='At least one function definition is required.', line=None))
    return diagnostics


def _preprocess(source):
    if re.search(r'\\\r?\n', source) or re.search(r'\?\?[=/\'()!<>-]', source):
        return source, [], [dict(severity='error', message='Line splicing and C trigraphs require a real preprocessor and are unsupported.', line=None)]
    # Strip comments without changing strings or source line numbers.
    token = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    def replace(match):
        spelling = match.group()
        if spelling.startswith(('//', '/*')):
            return ''.join('\n' if char == '\n' else ' ' for char in spelling)
        return spelling
    cleaned = token.sub(replace, source)
    headers, lines, diagnostics = [], [], []
    saw_code = False
    for number, line in enumerate(cleaned.splitlines(keepends=True), 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            if re.fullmatch(r'#\s*include\s*<(stdio|stdlib)\.h>\s*', stripped) and not saw_code:
                headers.append(stripped)
                lines.append('\n' if line.endswith('\n') else '')
            else:
                diagnostics.append(dict(severity='error', message='Only leading <stdio.h>/<stdlib.h> includes are supported. Other headers, macros, and conditional preprocessing require a real C frontend.', line=number))
                lines.append('\n' if line.endswith('\n') else '')
        else:
            lines.append(line)
            saw_code = saw_code or bool(stripped)
    if headers:
        diagnostics.append(dict(severity='warning', message='Header declarations are not analyzed. Leading #include directives are retained in emitted C; scalar-local restrictions still apply.', line=None))
    return ''.join(lines), headers, diagnostics


def _emit(tree, headers):
    prefix = '\n'.join(headers)
    return (prefix + '\n\n' if prefix else '') + _code(tree).rstrip() + '\n'


def optimize_source(source: str, pass_order=None, max_iterations=8):
    """Return JSON-safe source, pass trace, metrics, and explicit diagnostics.

    Supported data: lexical scalar int/unsigned int locals and parameters.
    Calls are preserved; without pointers or global data they cannot mutate a
    caller's scalar locals. Loop analysis deliberately sacrifices precision.
    This is a subset transformer, not a full C type checker or equivalence proof.
    """
    result = dict(status='error', diagnostics=[], original_code=source if isinstance(source, str) else '',
                  optimized_code=source if isinstance(source, str) else '', trace=[],
                  metrics=dict(original_ast_nodes=0, optimized_ast_nodes=0, passes_run=0, changed_passes=0))
    def fail(message, status='error', line=None):
        result['status'] = status
        result['diagnostics'].append(dict(severity='error', message=message, line=line))
        return result
    if not isinstance(source, str) or not source.strip():
        return fail('Provide nonempty C source text.')
    if len(source) > 100000:
        return fail('Source exceeds the 100,000 character limit for this educational optimizer.')
    order = list(PASS_NAMES) if pass_order is None else pass_order
    if not isinstance(order, (list, tuple)) or not order or len(order) > 32:
        return fail('pass_order must be a nonempty list of at most 32 pass names.')
    if any(not isinstance(name, str) or name not in PASS_NAMES for name in order):
        return fail('Unknown optimization pass. Choose: ' + ', '.join(PASS_NAMES) + '.')
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or not 1 <= max_iterations <= 30:
        return fail('max_iterations must be an integer between 1 and 30.')
    try:
        cleaned, headers, diagnostics = _preprocess(source)
        result['diagnostics'].extend(diagnostics)
        if any(item['severity'] == 'error' for item in diagnostics):
            result['status'] = 'unsupported'
            return result
        try:
            tree = c_parser.CParser().parse(cleaned, filename='<input>')
        except Exception as error:
            match = re.search(r':(\d+):', str(error))
            return fail('C parsing failed: ' + str(error), line=int(match.group(1)) if match else None)
        original_nodes = sum(1 for _ in _walk(tree))
        result['metrics']['original_ast_nodes'] = original_nodes
        result['metrics']['optimized_ast_nodes'] = original_nodes
        bindings = _Bindings(tree)
        diagnostics = _validate(tree, bindings)
        result['diagnostics'].extend(diagnostics)
        if any(item['severity'] == 'error' for item in diagnostics):
            result['status'] = 'unsupported'
            return result
        implementations = dict(propagation=_propagation, folding=_folding, dce=_dce, unused=_unused)
        last_iteration_changed = False
        for iteration in range(1, max_iterations + 1):
            iteration_changed = False
            for name in order:
                before = _emit(tree, headers)
                events = []
                bindings = _Bindings(tree)
                started = time.perf_counter()
                implementations[name](tree, bindings, events)
                duration_ms = round((time.perf_counter() - started) * 1000, 3)
                after = _emit(tree, headers)
                changed = before != after
                iteration_changed |= changed
                result['trace'].append(dict(index=len(result['trace']) + 1, iteration=iteration, pass_name=name,
                                            changed=changed, before=before, after=after, changes=events, duration_ms=duration_ms))
            last_iteration_changed = iteration_changed
            if not iteration_changed:
                break
        if last_iteration_changed:
            result['diagnostics'].append(dict(severity='warning', message='Stopped at the iteration limit; additional optimization opportunities may remain.', line=None))
        result['optimized_code'] = _emit(tree, headers)
        result['metrics'].update(optimized_ast_nodes=sum(1 for _ in _walk(tree)), passes_run=len(result['trace']),
                                 changed_passes=sum(item['changed'] for item in result['trace']))
        result['status'] = 'ok'
        return result
    except Exception as error:
        result['optimized_code'] = source
        return fail('Optimization failed safely: ' + type(error).__name__ + ': ' + str(error))
