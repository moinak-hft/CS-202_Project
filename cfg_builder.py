from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from pycparser import c_ast, c_generator

gen = c_generator.CGenerator()

@dataclass
class BasicBlock:
    id: str
    stmts: List[str] = field(default_factory=list)
    preds: List[str] = field(default_factory=list)
    succs: List[Tuple[str, str]] = field(default_factory=list)

    def add_stmt(self, stmt) -> None:
        self.stmts.append(gen.visit(stmt))

    def label(self) -> str:
        if not self.stmts:
            return self.id
        return f"{self.id}\\n" + "\\n".join(self.stmts)

class CFG:
    def __init__(self):
        self.blocks: Dict[str, BasicBlock] = {}
        self.entry: Optional[str] = None
        self.exit: Optional[str] = None

    def add_block(self, block: BasicBlock):
        self.blocks[block.id] = block

    def add_edge(self, src: str, dst: str, label: str = ""):
        self.blocks[src].succs.append((dst, label))
        self.blocks[dst].preds.append(src)

class CFGBuilder:
    def __init__(self):
        self.cfg = CFG()
        self.counter = 0

    def new_block(self) -> BasicBlock:
        bid = f"B{self.counter}"
        self.counter += 1
        block = BasicBlock(id=bid)
        self.cfg.add_block(block)
        return block

    def build_from_code(self, code: str) -> CFG:
        from pycparser import c_parser
        parser = c_parser.CParser()
        ast = parser.parse(code)

        for ext in ast.ext:
            if isinstance(ext, c_ast.FuncDef):
                self.cfg = CFG()
                self.counter = 0
                self._build_function(ext)
                return self.cfg

        raise ValueError("No function definition found in the input code.")

    def _build_function(self, func: c_ast.FuncDef):
        self.return_blocks = []
        entry = self.new_block()
        self.cfg.entry = entry.id

        exits = self._build_stmt_list(func.body.block_items or [], [entry.id])
        
        end = self.new_block()
        self.cfg.exit = end.id

        for b in exits + self.return_blocks:
            if b not in self.cfg.blocks[end.id].preds:
                self.cfg.add_edge(b, end.id, "fallthrough")

    def _build_stmt_list(self, stmts, incoming: List[str]) -> List[str]:
        current = incoming
        for stmt in stmts:
            if not current:
                current = [self.new_block().id]
            current = self._build_stmt(stmt, current)
        return current

    def _attach_stmt_to_blocks(self, block_ids: List[str], stmt) -> str:
        block = self.new_block()
        block.add_stmt(stmt)
        for pred in block_ids:
            self.cfg.add_edge(pred, block.id, "fallthrough")
        return block.id

    def _build_stmt(self, stmt, incoming: List[str]) -> List[str]:
        if isinstance(stmt, (c_ast.Decl, c_ast.Assignment, c_ast.FuncCall, c_ast.UnaryOp, c_ast.BinaryOp)):
            if len(incoming) == 1 and len(self.cfg.blocks[incoming[0]].succs) == 0:
                self.cfg.blocks[incoming[0]].add_stmt(stmt)
                return incoming
            else:
                return [self._attach_stmt_to_blocks(incoming, stmt)]

        if isinstance(stmt, c_ast.Return):
            if len(incoming) == 1 and len(self.cfg.blocks[incoming[0]].succs) == 0:
                self.cfg.blocks[incoming[0]].add_stmt(stmt)
                self.return_blocks.append(incoming[0])
            else:
                bid = self._attach_stmt_to_blocks(incoming, stmt)
                self.return_blocks.append(bid)
            return []

        if isinstance(stmt, c_ast.Compound):
            return self._build_stmt_list(stmt.block_items or [], incoming)

        if isinstance(stmt, c_ast.If):
            return self._build_if(stmt, incoming)

        if isinstance(stmt, c_ast.While):
            return self._build_while(stmt, incoming)

        if isinstance(stmt, c_ast.For):
            return self._build_for(stmt, incoming)

        bid = self._attach_stmt_to_blocks(incoming, stmt)
        return [bid]

    def _build_if(self, node: c_ast.If, incoming: List[str]) -> List[str]:
        cond_block = self.new_block()
        cond_block.add_stmt(node.cond)

        for pred in incoming:
            self.cfg.add_edge(pred, cond_block.id, "fallthrough")

        then_entry = self.new_block()
        self.cfg.add_edge(cond_block.id, then_entry.id, "true")

        then_exits = self._build_branch(node.iftrue, then_entry.id)

        join_block = self.new_block()

        if node.iffalse is not None:
            else_entry = self.new_block()
            self.cfg.add_edge(cond_block.id, else_entry.id, "false")
            else_exits = self._build_branch(node.iffalse, else_entry.id)
        else:
            else_exits = []
            self.cfg.add_edge(cond_block.id, join_block.id, "false")

        for b in then_exits:
            self.cfg.add_edge(b, join_block.id, "fallthrough")

        for b in else_exits:
            self.cfg.add_edge(b, join_block.id, "fallthrough")

        return [join_block.id]

    def _build_branch(self, branch_node, entry_block_id: str) -> List[str]:
        if isinstance(branch_node, c_ast.Compound):
            return self._build_stmt_list(branch_node.block_items or [], [entry_block_id])
        else:
            return self._build_stmt(branch_node, [entry_block_id])

    def _build_while(self, node: c_ast.While, incoming: List[str]) -> List[str]:
        cond_block = self.new_block()
        cond_block.add_stmt(node.cond)

        for pred in incoming:
            self.cfg.add_edge(pred, cond_block.id, "fallthrough")

        body_entry = self.new_block()
        self.cfg.add_edge(cond_block.id, body_entry.id, "true")

        body_exits = self._build_branch(node.stmt, body_entry.id)

        for b in body_exits:
            self.cfg.add_edge(b, cond_block.id, "back")

        after_loop = self.new_block()
        self.cfg.add_edge(cond_block.id, after_loop.id, "false")

        return [after_loop.id]

    def _build_for(self, node: c_ast.For, incoming: List[str]) -> List[str]:
        current = incoming

        if node.init is not None:
            init_block = self.new_block()
            init_block.add_stmt(node.init)
            for pred in current:
                self.cfg.add_edge(pred, init_block.id, "fallthrough")
            current = [init_block.id]

        cond_block = self.new_block()
        if node.cond is not None:
            cond_block.add_stmt(node.cond)

        for pred in current:
            self.cfg.add_edge(pred, cond_block.id, "fallthrough")

        body_entry = self.new_block()
        self.cfg.add_edge(cond_block.id, body_entry.id, "true")

        body_exits = self._build_branch(node.stmt, body_entry.id)

        if node.next is not None:
            next_block = self.new_block()
            next_block.add_stmt(node.next)
            for b in body_exits:
                self.cfg.add_edge(b, next_block.id, "fallthrough")
            self.cfg.add_edge(next_block.id, cond_block.id, "back")
        else:
            for b in body_exits:
                self.cfg.add_edge(b, cond_block.id, "back")

        after_loop = self.new_block()
        self.cfg.add_edge(cond_block.id, after_loop.id, "false")

        return [after_loop.id]
