from pathlib import Path
import shutil

import pycparser
from pycparser import parse_file, c_ast, c_generator
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot
from graphviz import Digraph

# Parse C through a real preprocessor so #define macros, #ifdef blocks,
# and includes are handled before pycparser builds the AST.
def find_preprocessor():
    for command, args in (
        ("clang", ["-E", "-P"]),
        ("gcc", ["-E", "-P"]),
        ("cpp", ["-P"]),
    ):
        path = shutil.which(command)
        if path:
            return path, args

    raise RuntimeError("No C preprocessor found. Install clang, gcc, or cpp.")

def get_fake_libc_include():
    candidates = [
        Path(pycparser.__file__).resolve().parent / "utils" / "fake_libc_include",
        Path(__file__).resolve().parent / "fake_libc_include",
    ]

    for fake_include in candidates:
        if fake_include.exists():
            return fake_include

    raise RuntimeError("fake_libc_include directory not found.")

def parse_c_file(filename):
    cpp_path, cpp_args = find_preprocessor()
    cpp_args = list(cpp_args)

    source_dir = Path(filename).resolve().parent
    fake_include = get_fake_libc_include()

    cpp_args.extend(["-nostdinc", "-I", str(fake_include)])

    cpp_args.extend(["-I", str(source_dir)])

    return parse_file(
        str(filename),
        use_cpp=True,
        cpp_path=cpp_path,
        cpp_args=cpp_args,
    )


#it will load the input.c file and expand macros using the C preprocessor
ast = parse_c_file("input.c")


######### Entering into constantfolder optimzation
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
                        val = l // r
                    elif node.op == '%':
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

                    return c_ast.Constant(type='int', value=str(val))

                except:
                    return node

        return node

def apply_constant_folding(ast):
    folder = ConstantFolder()
    folder.fold(ast)


######### Entering into constantPropagator optimization
class ConstantPropagator:

    def __init__(self):
        self.env = {}

    def propagate_expr(self, expr):

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

        return expr

    def visit(self, stmt):

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


######### Entering into SimpleDCE(dead code elimination)  
def is_constant_true(expr):
    return isinstance(expr, c_ast.Constant) and expr.value != '0'

def is_constant_false(expr):
    return isinstance(expr, c_ast.Constant) and expr.value == '0'

def is_exit_call(stmt):
    if isinstance(stmt, c_ast.FuncCall):
        if isinstance(stmt.name, c_ast.ID):
            return stmt.name.name in ["exit", "abort"]
    return False

class SimpleDCE:

    def process_block(self, block):
        if not block.block_items:
            return

        new_stmts = []
        terminated = False   

        for stmt in block.block_items:

            if terminated:
                continue   # it will remove everything after a return statement

            #if ke liye
            if isinstance(stmt, c_ast.If):

                
                cond = stmt.cond

                if is_constant_true(cond):
                    
                    self.process(stmt.iftrue)
                    new_stmts.append(stmt.iftrue)

                elif is_constant_false(cond):
                    
                    if stmt.iffalse:
                        self.process(stmt.iffalse)
                        new_stmts.append(stmt.iffalse)
                    

                else:
                    
                    self.process(stmt.iftrue)
                    if stmt.iffalse:
                        self.process(stmt.iffalse)
                    new_stmts.append(stmt)

            # while ke liye
            elif isinstance(stmt, c_ast.While):

                if is_constant_false(stmt.cond):
                    continue   

                self.process(stmt.stmt)
                new_stmts.append(stmt)

            # for ke liye
            elif isinstance(stmt, c_ast.For):

    
                if stmt.cond:
                    stmt.cond = stmt.cond

                # remove if always false
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

def apply_simple_dce(ast):
    dce = SimpleDCE()

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            dce.process(ext.body)


######### Entering into Unused Assignment Eliminator
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

    elif isinstance(expr, c_ast.TernaryOp):
        vars |= get_vars(expr.cond)
        vars |= get_vars(expr.iftrue)
        vars |= get_vars(expr.iffalse)

    elif isinstance(expr, c_ast.Cast):
        vars |= get_vars(expr.expr)

    elif isinstance(expr, c_ast.Assignment):
        vars |= get_vars(expr.lvalue)
        vars |= get_vars(expr.rvalue)

    elif isinstance(expr, c_ast.ArrayRef):
        vars |= get_vars(expr.name)
        vars |= get_vars(expr.subscript)

    elif isinstance(expr, c_ast.StructRef):
        vars |= get_vars(expr.name)
        vars |= get_vars(expr.field)

    elif isinstance(expr, c_ast.ExprList):
        for e in expr.exprs:
            vars |= get_vars(e)

    elif isinstance(expr, c_ast.FuncCall):
        vars |= get_vars(expr.name)
        if expr.args:
            for a in expr.args.exprs:
                vars |= get_vars(a)

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

                    # agr rhs kisi pr depend krta he to remove mt krna
                    if not rhs_vars:
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

                        #
                        if not rhs_vars:
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

            elif isinstance(stmt, c_ast.DoWhile):
                self.process(stmt.stmt)
                live |= get_vars(stmt.cond)
                new_stmts.append(stmt)

            
            elif isinstance(stmt, c_ast.For):
                self.process(stmt.stmt)
                if stmt.init:
                    self.process(stmt.init)
                if stmt.cond:
                    live |= get_vars(stmt.cond)
                if stmt.next:
                    live |= get_vars(stmt.next)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Switch):
                live |= get_vars(stmt.cond)
                new_stmts.append(stmt)

            elif isinstance(stmt, c_ast.Label):
                self.process(stmt.stmt)
                new_stmts.append(stmt)

            elif isinstance(stmt, (c_ast.Case, c_ast.Default)):
                if stmt.stmts:
                    case_block = c_ast.Compound(block_items=stmt.stmts)
                    self.process(case_block)
                    stmt.stmts = case_block.block_items
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

        elif isinstance(stmt, c_ast.DoWhile):
            self.process(stmt.stmt)

        elif isinstance(stmt, c_ast.For):
            if stmt.init:
                self.process(stmt.init)
            self.process(stmt.stmt)

        elif isinstance(stmt, c_ast.Switch):
            return

        elif isinstance(stmt, c_ast.Label):
            self.process(stmt.stmt)

        elif isinstance(stmt, (c_ast.Case, c_ast.Default)):
            if stmt.stmts:
                case_block = c_ast.Compound(block_items=stmt.stmts)
                self.process(case_block)
                stmt.stmts = case_block.block_items

def apply_unused_assignment_elimination(ast):
    uae = UnusedAssignmentEliminator()

    for ext in ast.ext:
        if isinstance(ext, c_ast.FuncDef):
            uae.process(ext.body)
code_generator = c_generator.CGenerator()

def code_to_str(node):
    if node is None:
        return ""

    return " ".join(code_generator.visit(node).split())

def stmt_to_str(stmt):
    text = code_to_str(stmt)
    if text and not text.endswith(";"):
        text += ";"
    return text

def expr_to_str(expr):
    return code_to_str(expr) or "expr"

def get_stmt_label(stmt):
    if isinstance(stmt, (c_ast.Assignment, c_ast.Decl, c_ast.Return, c_ast.FuncCall)):
        return stmt_to_str(stmt)
    elif isinstance(stmt, c_ast.If):
        return f"if ({expr_to_str(stmt.cond)})"
    elif isinstance(stmt, c_ast.While):
        return f"while ({expr_to_str(stmt.cond)})"
    elif isinstance(stmt, c_ast.DoWhile):
        return f"do while ({expr_to_str(stmt.cond)})"
    elif isinstance(stmt, c_ast.Switch):
        return f"switch ({expr_to_str(stmt.cond)})"
    return type(stmt).__name__


ast_graph = nx.DiGraph()
ast_id = 0

#build ast function
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

#Converting that function into ast.png
ast_pydot = to_pydot(ast_graph)
for n in ast_graph.nodes(data=True):
    ast_pydot.get_node(str(n[0]))[0].set_label(n[1]['label'])

ast_pydot.write_png("ast.png")

cfg = nx.DiGraph()
node_id = 0
cfg_stats = {}

######### Entering into CFG graph making
def new_node(label):
    global node_id
    nid = node_id
    node_id += 1
    cfg.add_node(nid, label=label)
    return nid

# entry Node Added
entry = new_node("ENTRY")

loop_break_targets = []
loop_continue_targets = []
label_nodes = {}
pending_gotos = []

def add_cfg_edges(from_nodes, to_node, label=None):
    if to_node is None:
        return

    for from_node in from_nodes:
        if label is None:
            cfg.add_edge(from_node, to_node)
        else:
            cfg.add_edge(from_node, to_node, label=label)

def resolve_gotos_to_label(label_name):
    global pending_gotos

    label_node = label_nodes[label_name]
    still_pending = []

    for goto_node, pending_label in pending_gotos:
        if pending_label == label_name:
            cfg.add_edge(goto_node, label_node)
        else:
            still_pending.append((goto_node, pending_label))

    pending_gotos = still_pending

def has_pending_goto(label_name):
    return any(pending_label == label_name for _, pending_label in pending_gotos)

def is_reachable_label(stmt):
    return isinstance(stmt, c_ast.Label) and (
        stmt.name in label_nodes or has_pending_goto(stmt.name)
    )

def build_statement_sequence(statements):
    if not statements:
        return None, []

    start = None
    prev_exits = []

    for s in statements:
        if start is not None and not prev_exits and not is_reachable_label(s):
            continue

        s_start, s_exits = build_cfg(s)

        if start is None:
            start = s_start

        add_cfg_edges(prev_exits, s_start)
        prev_exits = s_exits

    return start, prev_exits

def get_case_label(case_stmt):
    if isinstance(case_stmt, c_ast.Case):
        return f"case {expr_to_str(case_stmt.expr)}:"
    return "default:"

def get_switch_clauses(stmt):
    if isinstance(stmt.stmt, c_ast.Compound) and stmt.stmt.block_items:
        return [
            item for item in stmt.stmt.block_items
            if isinstance(item, (c_ast.Case, c_ast.Default))
        ]

    if isinstance(stmt.stmt, (c_ast.Case, c_ast.Default)):
        return [stmt.stmt]

    return []

def build_case_cfg(case_stmt):
    case_node = new_node(get_case_label(case_stmt))
    statements = case_stmt.stmts or []
    body_start, body_exits = build_statement_sequence(statements)

    if body_start:
        cfg.add_edge(case_node, body_start)
        return case_node, body_exits

    return case_node, [case_node]

def build_cfg(stmt):
    # Return value: (start_node, fallthrough_nodes).
    # fallthrough_nodes are only the nodes that can continue to the next statement.
    if stmt is None:
        return None, []

    if isinstance(stmt, c_ast.DeclList):
        if not stmt.decls:
            return None, []

        start = None
        prev_exits = []

        for decl in stmt.decls:
            decl_start, decl_exits = build_cfg(decl)

            if start is None:
                start = decl_start

            add_cfg_edges(prev_exits, decl_start)
            prev_exits = decl_exits

            if not prev_exits:
                break

        return start, prev_exits

    if isinstance(stmt, (c_ast.Decl, c_ast.Assignment, c_ast.FuncCall)):
        n = new_node(get_stmt_label(stmt))
        return n, [n]

    elif isinstance(stmt, c_ast.Return):
        n = new_node(get_stmt_label(stmt))
        return n, []

    elif isinstance(stmt, c_ast.Break):
        n = new_node("break;")
        if loop_break_targets:
            cfg.add_edge(n, loop_break_targets[-1])
        return n, []

    elif isinstance(stmt, c_ast.Continue):
        n = new_node("continue;")
        if loop_continue_targets:
            cfg.add_edge(n, loop_continue_targets[-1])
        return n, []

    elif isinstance(stmt, c_ast.Goto):
        n = new_node(f"goto {stmt.name};")
        if stmt.name in label_nodes:
            cfg.add_edge(n, label_nodes[stmt.name])
        else:
            pending_gotos.append((n, stmt.name))
        return n, []

    elif isinstance(stmt, c_ast.Label):
        label_node = label_nodes.get(stmt.name)

        if label_node is None:
            label_node = new_node(f"{stmt.name}:")
            label_nodes[stmt.name] = label_node

        resolve_gotos_to_label(stmt.name)

        stmt_start, stmt_exits = build_cfg(stmt.stmt)

        if stmt_start:
            cfg.add_edge(label_node, stmt_start)
            return label_node, stmt_exits

        return label_node, [label_node]

    # if case
    elif isinstance(stmt, c_ast.If):
        cond = new_node(get_stmt_label(stmt))

        then_start, then_exits = build_cfg(stmt.iftrue)
        if then_start is None:
            then_exits = [cond]

        if stmt.iffalse:
            else_start, else_exits = build_cfg(stmt.iffalse)
            if else_start is None:
                else_exits = [cond]
        else:
            else_start = None
            else_exits = [cond]

        if then_start:
            cfg.add_edge(cond, then_start, label="T")

        if else_start:
            cfg.add_edge(cond, else_start, label="F")

        fallthroughs = then_exits + else_exits

        if not fallthroughs:
            return cond, []

        merge = new_node("merge")
        add_cfg_edges(fallthroughs, merge)

        return cond, [merge]

    # while case
    elif isinstance(stmt, c_ast.While):
        cond = new_node(get_stmt_label(stmt))
        exit_node = new_node("exit while")

        loop_break_targets.append(exit_node)
        loop_continue_targets.append(cond)
        body_start, body_exits = build_cfg(stmt.stmt)
        loop_continue_targets.pop()
        loop_break_targets.pop()

        if body_start:
            cfg.add_edge(cond, body_start, label="T")

        add_cfg_edges(body_exits, cond)
        cfg.add_edge(cond, exit_node, label="F")

        return cond, [exit_node]

    # do-while case
    elif isinstance(stmt, c_ast.DoWhile):
        cond = new_node(f"do while ({expr_to_str(stmt.cond)})")
        exit_node = new_node("exit do while")

        loop_break_targets.append(exit_node)
        loop_continue_targets.append(cond)
        body_start, body_exits = build_cfg(stmt.stmt)
        loop_continue_targets.pop()
        loop_break_targets.pop()

        if body_start:
            add_cfg_edges([cond], body_start, label="T")
            add_cfg_edges(body_exits, cond)
            start = body_start
            exits = [exit_node] if cfg.in_degree(cond) > 0 else []
        else:
            start = cond
            exits = [exit_node]

        cfg.add_edge(cond, exit_node, label="F")

        return start, exits

    # switch/case/default case
    elif isinstance(stmt, c_ast.Switch):
        cond = new_node(f"switch ({expr_to_str(stmt.cond)})")
        exit_node = new_node("exit switch")
        clauses = get_switch_clauses(stmt)

        if not clauses:
            cfg.add_edge(cond, exit_node)
            return cond, [exit_node]

        loop_break_targets.append(exit_node)

        clause_cfgs = []
        has_default = False

        for clause in clauses:
            clause_start, clause_exits = build_case_cfg(clause)
            clause_cfgs.append((clause, clause_start, clause_exits))

            if isinstance(clause, c_ast.Default):
                has_default = True
                cfg.add_edge(cond, clause_start, label="default")
            elif isinstance(clause, c_ast.Case):
                cfg.add_edge(cond, clause_start, label=expr_to_str(clause.expr))

        loop_break_targets.pop()

        for i, (_, clause_start, clause_exits) in enumerate(clause_cfgs):
            if i + 1 < len(clause_cfgs):
                next_start = clause_cfgs[i + 1][1]
                add_cfg_edges(clause_exits, next_start)
            else:
                add_cfg_edges(clause_exits, exit_node)

        if not has_default:
            cfg.add_edge(cond, exit_node, label="default")

        if cfg.in_degree(exit_node) > 0:
            return cond, [exit_node]

        return cond, []

    # Compound
    elif isinstance(stmt, c_ast.Compound):
        return build_statement_sequence(stmt.block_items)

    elif isinstance(stmt, c_ast.For):

        if stmt.init:
            init_start, init_exits = build_cfg(stmt.init)
        else:
            init_start = None
            init_exits = []

        cond_label = "for"
        if stmt.cond:
            cond_label = f"for ({expr_to_str(stmt.cond)})"

        cond = new_node(cond_label)
        exit_node = new_node("exit for")

        if stmt.next:
            next_start, next_exits = build_cfg(stmt.next)
        else:
            next_start = None
            next_exits = []

        continue_target = next_start if next_start is not None else cond

        loop_break_targets.append(exit_node)
        loop_continue_targets.append(continue_target)
        body_start, body_exits = build_cfg(stmt.stmt)
        loop_continue_targets.pop()
        loop_break_targets.pop()

        if init_start is not None:
            add_cfg_edges(init_exits, cond)
        else:
            init_exits = [cond]

        if body_start:
            cfg.add_edge(cond, body_start, label="T")

        if next_start:
            add_cfg_edges(body_exits, next_start)
            add_cfg_edges(next_exits, cond)
        else:
            add_cfg_edges(body_exits, cond)

        cfg.add_edge(cond, exit_node, label="F")

        if init_start:
            return init_start, [exit_node]
        else:
            return cond, [exit_node]

    else:
        n = new_node(type(stmt).__name__)
        return n, [n]

def is_jump_terminator_label(label):
    return (
        label == "ENTRY"
        or label.startswith("return ")
        or label.startswith("goto ")
        or label in ("break;", "continue;")
    )

def is_label_node(label):
    return (
        label.endswith(":")
        or label.startswith("case ")
        or label == "default:"
    )

def is_artificial_cfg_label(label):
    return label == "merge" or label.startswith("exit ")

def find_basic_block_leaders(graph, entry_node):
    leaders = {entry_node}

    for node in graph.nodes:
        label = graph.nodes[node].get("label", "")

        if is_label_node(label):
            leaders.add(node)

        if graph.in_degree(node) != 1:
            leaders.add(node)

    for src, dst, data in graph.edges(data=True):
        src_label = graph.nodes[src].get("label", "")

        if graph.out_degree(src) != 1 or is_jump_terminator_label(src_label):
            leaders.add(dst)

        if "label" in data:
            leaders.add(dst)

    return leaders

def build_basic_block_label(block_id, block_nodes, graph):
    labels = [graph.nodes[node].get("label", "") for node in block_nodes]

    if labels == ["ENTRY"]:
        return "ENTRY"

    visible_labels = [
        label for label in labels
        if label and not is_artificial_cfg_label(label)
    ]

    if not visible_labels:
        visible_labels = [label for label in labels if label]

    return f"BB{block_id}\n" + "\n".join(visible_labels)

def collapse_to_basic_blocks(statement_graph, entry_node):
    leaders = find_basic_block_leaders(statement_graph, entry_node)
    visited = set()
    blocks = []

    for leader in sorted(leaders):
        if leader in visited:
            continue

        block_nodes = []
        current = leader

        while current is not None and current not in visited:
            block_nodes.append(current)
            visited.add(current)

            current_label = statement_graph.nodes[current].get("label", "")
            successors = list(statement_graph.successors(current))

            if len(successors) != 1:
                break

            successor = successors[0]
            edge_data = statement_graph.get_edge_data(current, successor, {})

            if "label" in edge_data:
                break

            if is_jump_terminator_label(current_label):
                break

            if successor in leaders:
                break

            if statement_graph.in_degree(successor) != 1:
                break

            current = successor

        if block_nodes:
            blocks.append(block_nodes)

    for node in sorted(statement_graph.nodes):
        if node not in visited:
            blocks.append([node])

    node_to_block = {}
    block_graph = nx.DiGraph()

    for block_id, block_nodes in enumerate(blocks):
        for node in block_nodes:
            node_to_block[node] = block_id

        block_graph.add_node(
            block_id,
            label=build_basic_block_label(block_id, block_nodes, statement_graph),
        )

    for src, dst, data in statement_graph.edges(data=True):
        src_block = node_to_block[src]
        dst_block = node_to_block[dst]

        if src_block == dst_block:
            continue

        edge_label = data.get("label")

        if block_graph.has_edge(src_block, dst_block):
            if edge_label:
                existing_label = block_graph[src_block][dst_block].get("label")
                if existing_label and edge_label not in existing_label.split(", "):
                    block_graph[src_block][dst_block]["label"] = f"{existing_label}, {edge_label}"
                elif not existing_label:
                    block_graph[src_block][dst_block]["label"] = edge_label
        elif edge_label:
            block_graph.add_edge(src_block, dst_block, label=edge_label)
        else:
            block_graph.add_edge(src_block, dst_block)

    return block_graph

def buildandsavecfggraphfinalwala(ast, filename, printingname):

   
    global cfg, node_id, entry
    cfg.clear()
    node_id = 0

   
    entry = new_node("ENTRY")

    astcopy = ast

    for ext in astcopy.ext:
        if isinstance(ext, c_ast.FuncDef):
            label_nodes.clear()
            pending_gotos.clear()
            loop_break_targets.clear()
            loop_continue_targets.clear()

            start, end = build_cfg(ext.body)

          
            if start is not None:
                cfg.add_edge(entry, start)

    statement_nodes = cfg.number_of_nodes()
    statement_edges = cfg.number_of_edges()
    cfg = collapse_to_basic_blocks(cfg, entry)

    # -------- SAVE CFG --------
    cfg_pydot = to_pydot(cfg)

    for n in cfg.nodes(data=True):
        cfg_pydot.get_node(str(n[0]))[0].set_label(n[1]['label'])
        if n[1]['label'] != "ENTRY":
            cfg_pydot.get_node(str(n[0]))[0].set_shape("box")
	
    for u, v, d in cfg.edges(data=True):
        if 'label' in d:
            edge = cfg_pydot.get_edge(str(u), str(v))[0]
            edge.set_label(d['label'])

    cfg_pydot.write_png(filename)

    cfg_stats[printingname] = {
        "nodes": cfg.number_of_nodes(),
        "edges": cfg.number_of_edges(),
        "statement_nodes": statement_nodes,
        "statement_edges": statement_edges,
    }
    print(
        f"{printingname}: "
        f"blocks={cfg_stats[printingname]['nodes']}, "
        f"edges={cfg_stats[printingname]['edges']} "
        f"(statement_nodes={statement_nodes}, statement_edges={statement_edges})"
    )

def print_cfg_comparison(before_name, after_name):
    if before_name not in cfg_stats or after_name not in cfg_stats:
        return

    before = cfg_stats[before_name]
    after = cfg_stats[after_name]

    print("\nCFG optimization summary")
    print(f"{before_name}: blocks={before['nodes']}, edges={before['edges']}")
    print(f"{after_name}: blocks={after['nodes']}, edges={after['edges']}")
    print(f"removed blocks={before['nodes'] - after['nodes']}")
    print(f"removed edges={before['edges'] - after['edges']}")


###### TEST CASES FOR DEBUGGING
# buildandsavecfggraphfinalwala(ast, "cfg_original.png", "hehe")
# apply_constant_folding(ast)
# buildandsavecfggraphfinalwala(ast, "cfg_fold1.png", "hehe")

# apply_constant_propagation(ast)
# buildandsavecfggraphfinalwala(ast, "cfg_propagation.png", "hehe")
# apply_constant_folding(ast)
# buildandsavecfggraphfinalwala(ast, "cfg_fold2.png", "hehe")

# apply_simple_dce(ast)   
# buildandsavecfggraphfinalwala(ast, "cfg_dce.png", "hehe")

# apply_unused_assignment_elimination(ast)
# buildandsavecfggraphfinalwala(ast, "cfg_unreachable.png", "hehe")




#final pipeline graph banane ka logic
def build_pipeline_graph(stages):

    g = Digraph(format='png')

    
    g.attr(rankdir='LR')

    for i, (name, img) in enumerate(stages):

        
        g.node(name, label="", image=img, shape='rectangle')

        if i > 0:
            prev_name = stages[i-1][0]

            
            if "prop" in name:
                label = f"{int(i/3)+1}_prop"
            elif "fold" in name:
                label = f"{int(i/3)+1}_fold"
            elif "dce" in name:
                label = f"{int(i/3)+1}_dce"
            else:
                label = "final_UAE"

            g.edge(prev_name, name, label=label)

    g.render("pipeline_graph")

#our pipeline for optimizing the cfg - collects stages and send to build_pipeline_graph -maximum iteration 50
def ast_to_string(ast):
    return str(ast)
def optimize_until_fixed(ast, max_iter=50):

    prev = None
    i = 0
    stages = []
    for _ in range(max_iter):
        i = i+1
        curr = ast_to_string(ast)

        if curr == prev:
            break

        prev = curr

        # propagation 
        apply_constant_propagation(ast)
        fname = f"cfg_iter_{i}_prop.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_prop")
        stages.append((f"iter{i}_prop", fname))

        # folding 
        apply_constant_folding(ast)
        fname = f"cfg_iter_{i}_fold.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_fold")
        stages.append((f"iter{i}_fold", fname))

        # dce 
        apply_simple_dce(ast)
        fname = f"cfg_iter_{i}_dce.png"
        buildandsavecfggraphfinalwala(ast, fname, f"{i}_dce")
        stages.append((f"iter{i}_dce", fname))


        
        



    apply_unused_assignment_elimination(ast)
    fname = f"cfg_iter_{i}_UAE.png"
    buildandsavecfggraphfinalwala(ast, fname, f"{i}_UAE")
    stages.append((f"iter{i}_UAE", fname))

    apply_constant_folding(ast)
    
    build_pipeline_graph(stages)
    return ast

# Pipeline
# (prop -> folding -> dce)ⁿ then uae



buildandsavecfggraphfinalwala(ast, "cfg_original.png", "original")
optimize_until_fixed(ast)
buildandsavecfggraphfinalwala(ast, "cfg_optimized.png", "final")
print_cfg_comparison("original", "final")





