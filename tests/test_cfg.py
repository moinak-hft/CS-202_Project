import unittest
from optilab.cfg import build_cfg, build_ast, CFGError

class CFGTests(unittest.TestCase):
    def graph(self, source):
        return build_cfg(source)["functions"][0]

    def test_return_is_a_terminator(self):
        graph = self.graph("int f(int x){if(x){return 1;}x=2;return x;}")
        nodes = {node["id"]: node for node in graph["nodes"]}
        for edge in graph["edges"]:
            if nodes[edge["source"]]["kind"] == "return":
                self.assertEqual(nodes[edge["target"]]["kind"], "exit")

    def test_loop_break_continue_have_targets(self):
        graph = self.graph("int f(int x){while(x){if(x==2)break;x=x-1;continue;}return x;}")
        nodes = {node["id"]: node for node in graph["nodes"]}
        for kind in ("break", "continue"):
            terminal = next(node for node in nodes.values() if node["kind"] == kind)
            successors = [nodes[e["target"]] for e in graph["edges"] if e["source"] == terminal["id"]]
            self.assertEqual(len(successors), 1)
            self.assertEqual(successors[0]["kind"], "condition" if kind == "continue" else "return")

    def test_unreachable_code_is_not_linked_after_return(self):
        graph = self.graph("int f(void){return 1;int x=2;}")
        declaration = next(node for node in graph["nodes"] if "x = 2" in node["label"])
        self.assertFalse(declaration["reachable"])

    def test_for_continue_runs_increment(self):
        graph = self.graph("int f(void){int x=0;for(int i=0;i<3;i++){continue;}return x;}")
        nodes = {node["id"]: node for node in graph["nodes"]}
        node = next(node for node in nodes.values() if node["kind"] == "continue")
        target = next(e["target"] for e in graph["edges"] if e["source"] == node["id"])
        self.assertIn("i++", nodes[target]["label"])

    def test_no_edges_between_functions(self):
        graphs = build_cfg("int f(void){return 1;}int g(void){return 2;}")["functions"]
        self.assertEqual([g["name"] for g in graphs], ["f", "g"])
        self.assertTrue(all(len(g["nodes"]) == 3 for g in graphs))

    def test_strings_survive_comment_cleanup(self):
        graph = build_ast('int f(void){puts("https://test");return 1;}')
        self.assertTrue(any("https://test" in n["label"] for n in graph["functions"][0]["nodes"]))

    def test_unsupported_goto_is_explicit(self):
        with self.assertRaises(CFGError):
            build_cfg("int f(void){goto out;out:return 0;}")

if __name__ == "__main__":
    unittest.main()
