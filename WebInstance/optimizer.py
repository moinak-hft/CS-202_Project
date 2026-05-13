from pycparser import c_parser, c_ast
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot
from graphviz import Digraph
import re

def preprocess_code(code):
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    macros = {}
    lines = code.splitlines()
    filtered = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#define"):
            parts = stripped.split(maxsplit=2)

            if len(parts) >= 3:
                macro_name = parts[1]
                macro_value = parts[2]
                macros[macro_name] = macro_value

            continue

        filtered.append(line)

    code = "\n".join(filtered)

    for macro_name, macro_value in macros.items():
        pattern = r'\b' + re.escape(macro_name) + r'\b'
        code = re.sub(pattern, macro_value, code)

    lines = code.splitlines()
    filtered = []

    for line in lines:
        if line.strip().startswith("#include"):
            continue

        filtered.append(line)

    return "\n".join(filtered)


with open("debug.c", "r") as f:
    code = f.read()

code = preprocess_code(code)
print(code)

parser = c_parser.CParser()
ast = parser.parse(code)


class ConstantFolder:
    def fold(self, node):
        if node is None:
            return None

        for child_name, child in node.children():
            new_child = self.fold(child)
            if new_child is not child:
                setattr(node, child_name, new_child)

        if isinstance(node, c_ast.BinaryOp):
            left = node.left
            right = node.right

            if isinstance(left, c_ast.Constant) and isinstance(right, c_ast.Constant):
                try:
                    l = int(left.value)
                    r = int(right.value)

                    if node.op == '+':
                        val = l + r
                    elif node.op == '-':
                        val = l - r
                    elif node.op == '*':
                        val = l * r
                    elif node.op == '/':
                        if r == 0:
                            return node
                        val = l / r
                    elif node.op == '%':
                        if r == 0:
                            return node
                        val = l % r
                    elif node.op == '>':
                        val = int(l > r)
                    elif node.op == '<':
                        val = int(l < r)
                    elif node.op == '>=':
                        val = int(l >= r)
                    elif node.op == '<=':
                        val = int(l <= r)
                    elif node.op == '==':
                        val = int(l == r)
                    else:
                        return node

                    return c_ast.Constant(type='int', value=str(int(val)))

                except:
                    return node

        return node

def apply_constant_folding(ast):
    folder = ConstantFolder()
    folder.fold(ast)


class ConstantPropagator:
    def __init__(self):
        self.env = {}

    def propagate_expr(self, expr):
        if expr is None:
            return None

        if isinstance(expr, c_ast.ID):
            if expr.name in self.env:
                val = self.env[expr.name]
                if isinstance(val, int):
                    return c_ast.Constant(type='int', value=str(val))
            return expr

        elif isinstance(expr, c_ast.BinaryOp):
            expr.left = self.propagate_expr(expr.left)
            expr.right = self.propagate_expr(expr.right)
            return expr

        elif isinstance(expr, c_ast.UnaryOp):
            if expr.op == '&':
                return expr

            expr.expr = self.propagate_expr(expr.expr)
            return expr

        elif isinstance(expr, c_ast.FuncCall):
            if expr.args:
                for i in range(len(expr.args.exprs)):
                    expr.args.exprs[i] = self.propagate_expr(expr.args.exprs[i])
            return expr

        elif isinstance(expr, c_ast.ExprList):
            for i in range(len(expr.exprs)):
                expr.exprs[i] = self.propagate_expr(expr.exprs[i])
            return expr

        return expr

    def visit(self, stmt):
        if stmt is None:
            return

        if isinstance(stmt, c_ast.Assignment):
            stmt.rvalue = self.propagate_expr(stmt.rvalue)

            if isinstance(stmt.rvalue, c_ast.Constant):
                self.env[stmt.lvalue.name] = int(stmt.rvalue.value)
            else:
                self.env[stmt.lvalue.name] = None

        elif isinstance(stmt, c_ast.Decl):
            if stmt.init:
                stmt.init = self.propagate_expr(stmt.init)

                if isinstance(stmt.init, c_ast.Constant):
                    self.env[stmt.name] = int(stmt.init.value)
                else:
                    self.env[stmt.name] = None

        elif isinstance(stmt, c_ast.FuncCall):
            self.propagate_expr(stmt)

        elif isinstance(stmt, c_ast.If):
            stmt.cond = self.propagate_expr(stmt.cond)

            old_env = self.env.copy()

            self.visit(stmt.iftrue)
            then_env = self.env.copy()

            self.env = old_env.copy()

            if stmt.iffalse:
                self.visit(stmt.iffalse)
                else_env = self.env.copy()
            else:
                else_env = old_env.copy()

            new_env = {}

            for var in set(list(then_env.keys()) + list(else_env.keys())):
                if then_env.get(var) == else_env.get(var):
                    new_env[var] = then_env.get(var)
                else:
                    new_env[var] = None

            self.env = new_env

        elif isinstance(stmt, c_ast.While):
            stmt.cond = self.propagate_expr(stmt.cond)

            old_env = self.env.copy()

            self.visit(stmt.stmt)

            loop_env = self.env.copy()
            new_env = {}

            for var in set(list(old_env.keys()) + list(loop_env.keys())):
                if old_env.get(var) == loop_env.get(var):
                    new_env[var] = old_env.get(var)
                else:
                    new_env[var] = None

            self.env = new_env

        elif isinstance(stmt, c_ast.Compound):
            if stmt.block_items:
                for s in stmt.block_items:
                    self.visit(s)

        elif isinstance(stmt, c_ast.Return):
            stmt.expr = self.propagate_expr(stmt.expr)

def apply_constant_propagation(ast):
    cp = ConstantPropagator()

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            cp.visit(ext.body)



def is_constant_true(expr):
    return isinstance(expr, c_ast.Constant) and expr.value != '0'
def is_constant_false(expr):
    return isinstance(expr, c_ast.Constant) and expr.value == '0'
def is_exit_call(stmt):
    if isinstance(stmt, c_ast.FuncCall):
        if isinstance(stmt.name, c_ast.ID):
            return stmt.name.name in ["exit", "abort"]
    return False
def always_terminates(stmt):
    if isinstance(stmt, c_ast.Return):
        return True

    if is_exit_call(stmt):
        return True

    if isinstance(stmt, c_ast.Compound):
        if not stmt.block_items:
            return False

        for s in stmt.block_items:
            if always_terminates(s):
                return True

        return False

    if isinstance(stmt, c_ast.If):
        if stmt.iffalse is None:
            return False

        return always_terminates(stmt.iftrue) and always_terminates(stmt.iffalse)

    return False
def has_side_effect(expr):
    if expr is None:
        return False

    if isinstance(expr, c_ast.FuncCall):
        return True

    if isinstance(expr, c_ast.Assignment):
        return True

    if isinstance(expr, c_ast.UnaryOp):
        if expr.op in ["p++", "p--", "++", "--"]:
            return True
        return has_side_effect(expr.expr)

    if isinstance(expr, c_ast.BinaryOp):
        return has_side_effect(expr.left) or has_side_effect(expr.right)

    if isinstance(expr, c_ast.ArrayRef):
        return has_side_effect(expr.name) or has_side_effect(expr.subscript)

    if isinstance(expr, c_ast.ExprList):
        return any(has_side_effect(e) for e in expr.exprs)

    return False

class SimpleDCE:
    def process_block(self, block):
        if not block.block_items:
            return

        new_stmts = []
        terminated = False

        for stmt in block.block_items:

            if terminated:
                continue

            if isinstance(stmt, c_ast.If):
                cond = stmt.cond

                if is_constant_true(cond):
                    self.process(stmt.iftrue)
                    new_stmts.append(stmt.iftrue)

                    if always_terminates(stmt.iftrue):
                        terminated = True

                elif is_constant_false(cond):
                    if stmt.iffalse:
                        self.process(stmt.iffalse)
                        new_stmts.append(stmt.iffalse)

                        if always_terminates(stmt.iffalse):
                            terminated = True

                else:
                    self.process(stmt.iftrue)

                    if stmt.iffalse:
                        self.process(stmt.iffalse)

                    new_stmts.append(stmt)

                    if stmt.iffalse and always_terminates(stmt.iftrue) and always_terminates(stmt.iffalse):
                        terminated = True

            elif isinstance(stmt, c_ast.While):
                if is_constant_false(stmt.cond):
                    continue

                self.process(stmt.stmt)
                new_stmts.append(stmt)

                if is_constant_true(stmt.cond) and always_terminates(stmt.stmt):
                    terminated = True

            elif isinstance(stmt, c_ast.For):
                if stmt.cond and is_constant_false(stmt.cond):
                    continue

                self.process(stmt.stmt)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Return):
                new_stmts.append(stmt)
                terminated = True

            elif is_exit_call(stmt):
                new_stmts.append(stmt)
                terminated = True

            elif isinstance(stmt, c_ast.Compound):
                self.process(stmt)
                new_stmts.append(stmt)

                if always_terminates(stmt):
                    terminated = True

            else:
                new_stmts.append(stmt)

        block.block_items = new_stmts

    def process(self, stmt):
        if isinstance(stmt, c_ast.Compound):
            self.process_block(stmt)

        elif isinstance(stmt, c_ast.If):
            self.process(stmt.iftrue)

            if stmt.iffalse:
                self.process(stmt.iffalse)

        elif isinstance(stmt, c_ast.While):
            self.process(stmt.stmt)

        elif isinstance(stmt, c_ast.For):
            self.process(stmt.stmt)

def apply_simple_dce(ast):
    dce = SimpleDCE()

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            dce.process(ext.body)



def get_vars(expr):
    vars = set()

    if expr is None:
        return vars

    if isinstance(expr, c_ast.ID):
        vars.add(expr.name)

    elif isinstance(expr, c_ast.BinaryOp):
        vars |= get_vars(expr.left)
        vars |= get_vars(expr.right)

    elif isinstance(expr, c_ast.UnaryOp):
        vars |= get_vars(expr.expr)

    elif isinstance(expr, c_ast.ArrayRef):
        vars |= get_vars(expr.name)
        vars |= get_vars(expr.subscript)

    elif isinstance(expr, c_ast.FuncCall):
        if expr.args:
            for a in expr.args.exprs:
                vars |= get_vars(a)

    elif isinstance(expr, c_ast.ExprList):
        for e in expr.exprs:
            vars |= get_vars(e)

    return vars

class UnusedAssignmentEliminator:
    def process_block(self, block):
        if not block.block_items:
            return

        live = set()
        new_stmts = []

        for stmt in reversed(block.block_items):

            if isinstance(stmt, c_ast.Assignment):
                lhs = stmt.lvalue.name
                rhs_vars = get_vars(stmt.rvalue)

                if lhs not in live:
                    live |= rhs_vars

                    if not rhs_vars and not has_side_effect(stmt.rvalue):
                        continue

                    new_stmts.append(stmt)
                    continue

                live.discard(lhs)
                live |= rhs_vars
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Decl):
                if stmt.init:
                    lhs = stmt.name
                    rhs_vars = get_vars(stmt.init)

                    if lhs not in live:
                        live |= rhs_vars

                        if not rhs_vars and not has_side_effect(stmt.init):
                            continue

                        new_stmts.append(stmt)
                        continue

                    live.discard(lhs)
                    live |= rhs_vars
                    new_stmts.append(stmt)
                else:
                    new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Return):
                if stmt.expr:
                    live |= get_vars(stmt.expr)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.FuncCall):
                live |= get_vars(stmt)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.If):
                self.process(stmt.iftrue)

                if stmt.iffalse:
                    self.process(stmt.iffalse)

                live |= get_vars(stmt.cond)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.While):
                self.process(stmt.stmt)
                live |= get_vars(stmt.cond)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.For):
                self.process(stmt.stmt)

                if stmt.cond:
                    live |= get_vars(stmt.cond)

                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Compound):
                self.process(stmt)
                new_stmts.append(stmt)

            else:
                new_stmts.append(stmt)

        block.block_items = list(reversed(new_stmts))

    def process(self, stmt):
        if isinstance(stmt, c_ast.Compound):
            self.process_block(stmt)

        elif isinstance(stmt, c_ast.If):
            self.process(stmt.iftrue)

            if stmt.iffalse:
                self.process(stmt.iffalse)

        elif isinstance(stmt, c_ast.While):
            self.process(stmt.stmt)

        elif isinstance(stmt, c_ast.For):
            self.process(stmt.stmt)

def apply_unused_assignment_elimination(ast):
    uae = UnusedAssignmentEliminator()

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            uae.process(ext.body)


def expr_to_str(expr):
    if expr is None:
        return ""

    if isinstance(expr, c_ast.Constant):
        return expr.value

    elif isinstance(expr, c_ast.ID):
        return expr.name

    elif isinstance(expr, c_ast.BinaryOp):
        return f"{expr_to_str(expr.left)} {expr.op} {expr_to_str(expr.right)}"

    elif isinstance(expr, c_ast.Assignment):
        return f"{expr_to_str(expr.lvalue)} = {expr_to_str(expr.rvalue)}"

    elif isinstance(expr, c_ast.UnaryOp):
        if expr.op in ['p++', 'p--']:
            return f"{expr_to_str(expr.expr)}{expr.op[1:]}"
        return f"{expr.op}{expr_to_str(expr.expr)}"

    elif isinstance(expr, c_ast.FuncCall):
        args = ""

        if expr.args:
            args = ", ".join(expr_to_str(a) for a in expr.args.exprs)

        return f"{expr_to_str(expr.name)}({args})"

    elif isinstance(expr, c_ast.ExprList):
        return ", ".join(expr_to_str(e) for e in expr.exprs)

    return "expr"

def get_stmt_label(stmt):
    if isinstance(stmt, c_ast.Assignment):
        return f"{expr_to_str(stmt.lvalue)} = {expr_to_str(stmt.rvalue)};"

    elif isinstance(stmt, c_ast.Decl):
        if stmt.init:
            return f"{stmt.name} = {expr_to_str(stmt.init)};"
        return f"int {stmt.name};"

    elif isinstance(stmt, c_ast.Return):
        return f"return {expr_to_str(stmt.expr)};"

    elif isinstance(stmt, c_ast.If):
        return f"if ({expr_to_str(stmt.cond)})"

    elif isinstance(stmt, c_ast.While):
        return f"while ({expr_to_str(stmt.cond)})"

    elif isinstance(stmt, c_ast.FuncCall):
        return f"{expr_to_str(stmt)};"

    return type(stmt).__name__


ast_graph = nx.DiGraph()
ast_id = 0


def build_ast_graph(node, parent=None):
    global ast_id
    curr = ast_id
    ast_id += 1

    label = type(node).__name__
    ast_graph.add_node(curr, label=label)

    if parent is not None:
        ast_graph.add_edge(parent, curr)

    for _, child in node.children():
        build_ast_graph(child, curr)
        
build_ast_graph(ast)

ast_pydot = to_pydot(ast_graph)

for n in ast_graph.nodes(data=True):
    ast_pydot.get_node(str(n[0]))[0].set_label(n[1]['label'])

ast_pydot.write_png("ast.png")


cfg = nx.DiGraph()
node_id = 0
function_nodes = {}


def new_node(label):
    global node_id
    nid = node_id
    node_id += 1
    cfg.add_node(nid, label=label)
    return nid


entry = new_node("ENTRY")


def build_cfg(stmt):
    if isinstance(stmt, (c_ast.Decl, c_ast.Assignment, c_ast.FuncCall)):
        n = new_node(get_stmt_label(stmt))
        return n, n

    elif isinstance(stmt, c_ast.Return):
        n = new_node(get_stmt_label(stmt))
        return n, n

    elif isinstance(stmt, c_ast.If):
        cond = new_node(get_stmt_label(stmt))

        then_start, then_end = build_cfg(stmt.iftrue)

        if stmt.iffalse:
            else_start, else_end = build_cfg(stmt.iffalse)
        else:
            else_start = else_end = None

        if then_start:
            cfg.add_edge(cond, then_start, label="T")

        if else_start:
            cfg.add_edge(cond, else_start, label="F")

        merge = new_node("merge")

        if then_end:
            cfg.add_edge(then_end, merge)

        if else_end:
            cfg.add_edge(else_end, merge)

        if stmt.iffalse is None:
            cfg.add_edge(cond, merge, label="F")

        return cond, merge

    elif isinstance(stmt, c_ast.While):
        cond = new_node(get_stmt_label(stmt))

        body_start, body_end = build_cfg(stmt.stmt)

        if body_start:
            cfg.add_edge(cond, body_start, label="T")

        if body_end:
            cfg.add_edge(body_end, cond)

        exit_node = new_node("exit while")
        cfg.add_edge(cond, exit_node, label="F")

        return cond, exit_node

    elif isinstance(stmt, c_ast.Compound):
        if not stmt.block_items:
            return None, None

        start = None
        prev_end = None

        for s in stmt.block_items:
            s_start, s_end = build_cfg(s)

            if start is None:
                start = s_start

            if prev_end is not None and s_start is not None:
                cfg.add_edge(prev_end, s_start)

            prev_end = s_end

        return start, prev_end

    elif isinstance(stmt, c_ast.For):
        if stmt.init:
            init_start, init_end = build_cfg(stmt.init)
        else:
            init_start = init_end = None

        cond_label = "for"

        if stmt.cond:
            cond_label = f"for ({expr_to_str(stmt.cond)})"

        cond = new_node(cond_label)

        body_start, body_end = build_cfg(stmt.stmt)

        if stmt.next:
            next_start, next_end = build_cfg(stmt.next)
        else:
            next_start = next_end = None

        if init_end is not None:
            cfg.add_edge(init_end, cond)
        elif init_start is not None:
            cfg.add_edge(init_start, cond)

        if body_start:
            cfg.add_edge(cond, body_start, label="T")

        if body_end and next_start:
            cfg.add_edge(body_end, next_start)

        if next_end:
            cfg.add_edge(next_end, cond)
        elif body_end:
            cfg.add_edge(body_end, cond)

        exit_node = new_node("exit for")
        cfg.add_edge(cond, exit_node, label="F")

        if init_start:
            return init_start, exit_node
        else:
            return cond, exit_node

    else:
        n = new_node(type(stmt).__name__)
        return n, n

def buildandsavecfggraphfinalwala(ast, filename, printingname):
    global cfg, node_id, entry, function_nodes

    cfg.clear()
    node_id = 0
    function_nodes = {}

    entry = new_node("ENTRY")

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            function_nodes[ext.decl.name] = new_node(f"{ext.decl.name}()")

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            func_node = function_nodes[ext.decl.name]
            start, end = build_cfg(ext.body)

            if start is not None:
                cfg.add_edge(func_node, start)

            if ext.decl.name == "main":
                cfg.add_edge(entry, func_node)

    cfg_pydot = to_pydot(cfg)

    for n in cfg.nodes(data=True):
        cfg_pydot.get_node(str(n[0]))[0].set_label(n[1]['label'])

    for u, v, d in cfg.edges(data=True):
        if 'label' in d:
            edge = cfg_pydot.get_edge(str(u), str(v))[0]
            edge.set_label(d['label'])

    cfg_pydot.write_png(filename)

    print(printingname)

def build_pipeline_graph(stages):
    g = Digraph(format='png')
    g.attr(rankdir='LR')

    for i, (name, img) in enumerate(stages):
        g.node(name, label="", image=img, shape='rectangle')

        if i > 0:
            prev_name = stages[i - 1][0]

            if "prop" in name:
                label = f"{int(i / 3) + 1}_prop"
            elif "fold" in name:
                label = f"{int(i / 3) + 1}_fold"
            elif "dce" in name:
                label = f"{int(i / 3) + 1}_dce"
            else:
                label = "final_UAE"

            g.edge(prev_name, name, label=label)

    g.render("pipeline_graph")

def ast_to_string(ast):
    return str(ast)

def optimize_until_fixed(ast, max_iter=50):
    prev = None
    i = 0
    stages = []

    for _ in range(max_iter):
        i = i + 1
        curr = ast_to_string(ast)

        if curr == prev:
            break

        prev = curr

        apply_constant_propagation(ast)
        fname = f"cfg_iter_{i}_prop.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_prop")
        stages.append((f"iter{i}_prop", fname))

        apply_constant_folding(ast)
        fname = f"cfg_iter_{i}_fold.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_fold")
        stages.append((f"iter{i}_fold", fname))

        apply_simple_dce(ast)
        fname = f"cfg_iter_{i}_dce.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_dce")
        stages.append((f"iter{i}_dce", fname))

    apply_constant_propagation(ast)
    apply_constant_folding(ast)
    apply_unused_assignment_elimination(ast)
    apply_simple_dce(ast)

    fname = f"cfg_iter_{i}_UAE.png"
    buildandsavecfggraphfinalwala(ast, fname, f"{i}_UAE")
    stages.append((f"iter{i}_UAE", fname))

    build_pipeline_graph(stages)
    return ast


buildandsavecfggraphfinalwala(ast, "cfg_original.png", "original")
optimize_until_fixed(ast)
buildandsavecfggraphfinalwala(ast, "cfg_optimized.png", "final")
