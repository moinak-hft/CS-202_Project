"""Structured, per-function CFGs without Graphviz or import-time effects."""
from collections import deque
import re
from pycparser import c_ast, c_generator, c_parser

class CFGError(ValueError):
    pass

def _line(node):
    return getattr(getattr(node, "coord", None), "line", None)

def _parse(source):
    # Preserve source coordinates and comment-looking text inside C strings.
    token = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/', re.S)
    def clean(match):
        text = match.group()
        return text if text[0] in "\"'" else "".join("\n" if ch == "\n" else " " for ch in text)
    source = token.sub(clean, source)
    lines = []
    for line in source.splitlines(keepends=True):
        if line.lstrip().startswith("#include"):
            lines.append("\n" if line.endswith("\n") else "")
        elif line.lstrip().startswith("#"):
            raise CFGError("Preprocess macros before building a control-flow graph.")
        else:
            lines.append(line)
    try:
        return c_parser.CParser().parse("".join(lines))
    except Exception as error:
        raise CFGError(str(error)) from error

class _Builder:
    def __init__(self, function):
        self.function = function
        self.nodes, self.edges = [], []
        self.gen = c_generator.CGenerator()
        self.entry = self.add("ENTRY " + function.decl.name, "entry", function)
        self.exit = self.add("EXIT " + function.decl.name, "exit", function)

    def add(self, label, kind, node=None):
        identifier = str(len(self.nodes))
        self.nodes.append(dict(id=identifier, label=label, kind=kind, line=_line(node)))
        return identifier

    def edge(self, source, target, label=""):
        if target is not None:
            item = dict(source=source, target=target, label=label)
            if item not in self.edges:
                self.edges.append(item)

    def statement(self, stmt, following, break_target=None, continue_target=None):
        if stmt is None:
            return following
        if isinstance(stmt, c_ast.Compound):
            result = following
            for child in reversed(stmt.block_items or []):
                result = self.statement(child, result, break_target, continue_target)
            return result
        if isinstance(stmt, c_ast.Return):
            result = self.add(self.gen.visit(stmt), "return", stmt)
            self.edge(result, self.exit, "return")
            return result
        if isinstance(stmt, c_ast.Break):
            if break_target is None:
                raise CFGError("break has no enclosing supported loop.")
            result = self.add("break", "break", stmt)
            self.edge(result, break_target, "break")
            return result
        if isinstance(stmt, c_ast.Continue):
            if continue_target is None:
                raise CFGError("continue has no enclosing loop.")
            result = self.add("continue", "continue", stmt)
            self.edge(result, continue_target, "continue")
            return result
        if isinstance(stmt, c_ast.If):
            result = self.add("if (" + self.gen.visit(stmt.cond) + ")", "condition", stmt)
            yes = self.statement(stmt.iftrue, following, break_target, continue_target)
            no = self.statement(stmt.iffalse, following, break_target, continue_target)
            self.edge(result, yes, "T")
            self.edge(result, no, "F")
            return result
        if isinstance(stmt, (c_ast.While, c_ast.DoWhile)):
            result = self.add(("do / while" if isinstance(stmt, c_ast.DoWhile) else "while") +
                              " (" + self.gen.visit(stmt.cond) + ")", "condition", stmt)
            body = self.statement(stmt.stmt, result, following, result)
            self.edge(result, body, "T")
            self.edge(result, following, "F")
            return body if isinstance(stmt, c_ast.DoWhile) else result
        if isinstance(stmt, c_ast.For):
            result = self.add("for (" + (self.gen.visit(stmt.cond) if stmt.cond else "true") + ")", "condition", stmt)
            increment = self.statement(stmt.next, result, following, result) if stmt.next else result
            body = self.statement(stmt.stmt, increment, following, increment)
            self.edge(result, body, "T")
            if stmt.cond is not None:
                self.edge(result, following, "F")
            return self.statement(stmt.init, result, following, increment) if stmt.init else result
        if isinstance(stmt, c_ast.DeclList):
            result = following
            for child in reversed(stmt.decls):
                result = self.statement(child, result, break_target, continue_target)
            return result
        if isinstance(stmt, (c_ast.Switch, c_ast.Case, c_ast.Default, c_ast.Goto, c_ast.Label)):
            raise CFGError(type(stmt).__name__ + " control flow is not supported by this graph builder.")
        result = self.add(self.gen.visit(stmt).strip() or ";", "statement", stmt)
        self.edge(result, following)
        return result

    def build(self):
        first = self.statement(self.function.body, self.exit)
        self.edge(self.entry, first)
        adjacency = {}
        for edge in self.edges:
            adjacency.setdefault(edge["source"], []).append(edge["target"])
        order, seen, queue = [], set(), deque([self.entry])
        while queue:
            node = queue.popleft()
            if node in seen:
                continue
            seen.add(node)
            order.append(node)
            queue.extend(adjacency.get(node, []))
        by_id = {node["id"]: node for node in self.nodes}
        nodes = [by_id[node] for node in order] + [node for node in self.nodes if node["id"] not in seen]
        for node in nodes:
            node["reachable"] = node["id"] in seen
        return dict(name=self.function.decl.name, nodes=nodes, edges=self.edges)

def build_cfg(source):
    """Return structural CFGs. Reachability is graph reachability, not path feasibility."""
    if not isinstance(source, str) or not source.strip():
        raise CFGError("C source is required.")
    if len(source) > 100_000:
        raise CFGError("C source exceeds 100,000 characters.")
    tree = _parse(source)
    return dict(functions=[_Builder(node).build() for node in tree.ext if isinstance(node, c_ast.FuncDef)],
                model="structural per-function CFG; expressions are atomic; branches are not path-sensitive")

def build_ast(source):
    """Return a compact AST graph for tools that consume structured graph data."""
    tree = _parse(source)
    nodes, edges = [], []
    def visit(node, parent=None, field=""):
        identifier = str(len(nodes))
        attrs = ", ".join(str(getattr(node, attr)) for attr in node.attr_names if getattr(node, attr) is not None)
        nodes.append(dict(id=identifier, label=type(node).__name__ + (": " + attrs if attrs else ""), line=_line(node), kind="ast"))
        if parent is not None:
            edges.append(dict(source=parent, target=identifier, label=field))
        for name, child in node.children():
            visit(child, identifier, name)
    visit(tree)
    return dict(functions=[dict(name="AST", nodes=nodes, edges=edges)], model="pycparser abstract syntax tree")
