#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Analysis/CFG.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/AST/Stmt.h"
#include "clang/AST/PrettyPrinter.h"
#include "clang/Basic/LangOptions.h"
#include <string>
#include <algorithm>

using namespace clang;
using namespace clang::tooling;
using namespace llvm;

class CFGVisitor : public RecursiveASTVisitor<CFGVisitor> {
public:
    explicit CFGVisitor(ASTContext *Context) : Context(Context) {}

    bool VisitFunctionDecl(FunctionDecl *Declaration) {
        if (!Declaration->hasBody()) return true;

        CFG::BuildOptions Options;
        std::unique_ptr<CFG> sourceCFG =
            CFG::buildCFG(Declaration, Declaration->getBody(), Context, Options);

        if (!sourceCFG) return true;

        outs() << "digraph CFG {\n";
        outs() << "  node [shape=box];\n";

        LangOptions LO;
        LO.CPlusPlus = 1;
        PrintingPolicy Policy(LO);

        for (auto *block : *sourceCFG) {
            if (!block) continue;

            int src_id = block->getBlockID();
            std::string label = "B" + std::to_string(src_id) + "\\n";

            for (auto &E : *block) {
                if (std::optional<CFGStmt> CS = E.getAs<CFGStmt>()) {
                    const Stmt *S = CS->getStmt();
                    std::string stmtStr;
                    llvm::raw_string_ostream rso(stmtStr);
                    S->printPretty(rso, nullptr, Policy);
                    
                    std::string cleanStr = rso.str();
                    std::replace(cleanStr.begin(), cleanStr.end(), '\n', ' ');
                    std::replace(cleanStr.begin(), cleanStr.end(), '"', '\'');
                    
                    label += cleanStr + "\\n";
                }
            }

            outs() << "  B" << src_id << " [label=\"" << label << "\"];\n";

            unsigned succ_idx = 0;
            for (auto I = block->succ_begin(), E = block->succ_end(); I != E; ++I, ++succ_idx) {
                if (CFGBlock *dst = I->getReachableBlock()) {
                    std::string edge_label = "fallthrough";
                    
                    if (block->getTerminatorStmt()) {
                        if (succ_idx == 0) edge_label = "true";
                        else if (succ_idx == 1) edge_label = "false";
                    }
                    
                    outs() << "  B" << src_id << " -> B" << dst->getBlockID() 
                           << " [label=\"" << edge_label << "\"];\n";
                }
            }
        }

        outs() << "}\n";
        return true;
    }

private:
    ASTContext *Context;
};

class CFGConsumer : public ASTConsumer {
public:
    explicit CFGConsumer(ASTContext *Context) : Visitor(Context) {}

    void HandleTranslationUnit(ASTContext &Context) override {
        Visitor.TraverseDecl(Context.getTranslationUnitDecl());
    }

private:
    CFGVisitor Visitor;
};

class CFGAction : public ASTFrontendAction {
public:
    std::unique_ptr<ASTConsumer> CreateASTConsumer(
        CompilerInstance &Compiler, StringRef InFile) override {
        return std::make_unique<CFGConsumer>(&Compiler.getASTContext());
    }
};

static cl::OptionCategory CFGCategory("CFG Generator");

int main(int argc, const char **argv) {
    auto ExpectedParser = CommonOptionsParser::create(argc, argv, CFGCategory);
    if (!ExpectedParser) {
        errs() << ExpectedParser.takeError();
        return 1;
    }

    CommonOptionsParser &OptionsParser = ExpectedParser.get();
    ClangTool Tool(OptionsParser.getCompilations(),
                   OptionsParser.getSourcePathList());

    return Tool.run(newFrontendActionFactory<CFGAction>().get());
}