import networkx as nx
from networkx.drawing.nx_pydot import to_pydot

def export_cfg_to_dot(cfg, filename="cfg.dot"):
    G = nx.DiGraph()

    for bid, block in cfg.blocks.items():
        G.add_node(bid, label=block.label(), shape="box")

    for bid, block in cfg.blocks.items():
        for succ, label in block.succs:
            G.add_edge(bid, succ, label=label)

    pydot_graph = to_pydot(G)
    pydot_graph.write_raw(filename)

def export_cfg_to_png(cfg, filename="cfg.png"):
    G = nx.DiGraph()

    for bid, block in cfg.blocks.items():
        G.add_node(bid, label=block.label(), shape="box")

    for bid, block in cfg.blocks.items():
        for succ, label in block.succs:
            G.add_edge(bid, succ, label=label)

    pydot_graph = to_pydot(G)
    pydot_graph.write_png(filename)
