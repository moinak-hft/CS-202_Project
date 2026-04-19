from cfg_builder import CFGBuilder
from visualize import export_cfg_to_dot, export_cfg_to_png

sample_code = r"""
int f(int x) {
    int a = 0;
    if (x > 0) {
        a = 1;
    } else {
        a = 2;
    }

    while (a < 5) {
        a = a + 1;
    }

    return a;
}
"""

def print_cfg(cfg):
    print("ENTRY:", cfg.entry)
    print("EXIT:", cfg.exit)
    print()

    for bid, block in cfg.blocks.items():
        print(f"{bid}:")
        for s in block.stmts:
            print("   ", s)
        print("   preds:", block.preds)
        print("   succs:", block.succs)
        print()

def main():
    builder = CFGBuilder()
    cfg = builder.build_from_code(sample_code)

    print_cfg(cfg)
    export_cfg_to_dot(cfg, "cfg.dot")
    export_cfg_to_png(cfg, "cfg.png")
    print("CFG exported to cfg.dot and cfg.png")

if __name__ == "__main__":
    main()
