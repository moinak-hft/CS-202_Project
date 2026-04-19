#include <vector>
#include <set>
#include <map>
#include <stack>
#include <string>

struct Statement {
    std::string lhs;
    std::vector<std::string> rhs_operands;
};

struct PhiFunction {
    std::string original_var;
    std::string assigned_var;
    std::map<int, std::string> incoming;
};

struct Block {
    int id;
    std::vector<Block*> predecessors;
    std::vector<Block*> successors;
    Block* immediate_dominator = nullptr;
    std::vector<Block*> dominator_children;
    std::set<Block*> dominance_frontier;
    std::set<std::string> defined_vars;
    std::vector<PhiFunction> phi_functions;
    std::vector<Statement> statements;
};

void insertPhiFunctions(std::vector<Block*>& cfg, const std::vector<std::string>& global_vars) {
    for (const std::string& v : global_vars) {
        std::set<Block*> worklist;
        std::set<Block*> ever_on_worklist;
        std::set<Block*> has_already;

        for (Block* b : cfg) {
            if (b->defined_vars.count(v)) {
                worklist.insert(b);
                ever_on_worklist.insert(b);
            }
        }

        while (!worklist.empty()) {
            Block* x = *worklist.begin();
            worklist.erase(worklist.begin());

            for (Block* y : x->dominance_frontier) {
                if (!has_already.count(y)) {
                    PhiFunction phi;
                    phi.original_var = v;
                    y->phi_functions.push_back(phi);
                    has_already.insert(y);

                    if (!ever_on_worklist.count(y)) {
                        ever_on_worklist.insert(y);
                        worklist.insert(y);
                    }
                }
            }
        }
    }
}

std::map<std::string, std::stack<int>> var_stacks;
std::map<std::string, int> var_counters;

std::string getNewVarName(const std::string& var) {
    int count = var_counters[var]++;
    var_stacks[var].push(count);
    return var + "_" + std::to_string(count);
}

void renameVariables(Block* b) {
    std::map<std::string, int> pop_counts;

    for (PhiFunction& phi : b->phi_functions) {
        phi.assigned_var = getNewVarName(phi.original_var);
        pop_counts[phi.original_var]++;
    }

    for (Statement& stmt : b->statements) {
        for (std::string& rhs : stmt.rhs_operands) {
            if (!var_stacks[rhs].empty()) {
                rhs = rhs + "_" + std::to_string(var_stacks[rhs].top());
            }
        }
        if (!stmt.lhs.empty()) {
            std::string orig_lhs = stmt.lhs;
            stmt.lhs = getNewVarName(stmt.lhs);
            pop_counts[orig_lhs]++;
        }
    }

    for (Block* succ : b->successors) {
        for (PhiFunction& succ_phi : succ->phi_functions) {
            if (!var_stacks[succ_phi.original_var].empty()) {
                succ_phi.incoming[b->id] = succ_phi.original_var + "_" + std::to_string(var_stacks[succ_phi.original_var].top());
            }
        }
    }

    for (Block* child : b->dominator_children) {
        renameVariables(child);
    }

    for (const auto& pair : pop_counts) {
        for (int i = 0; i < pair.second; ++i) {
            var_stacks[pair.first].pop();
        }
    }
}
