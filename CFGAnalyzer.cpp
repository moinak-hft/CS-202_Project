#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Analysis/CFG.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"

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

        for (auto *block : *sourceCFG) {
            if (!block) continue;

            int src_id = block->getBlockID();


            outs() << "  B" << src_id << " [label=\"B" << src_id << "\"];\n";

            
            for (auto succ : block->succs()) {
                if (succ.getReachableBlock()) {
                    int dst_id = succ.getReachableBlock()->getBlockID();
                    outs() << "  B" << src_id << " -> B" << dst_id << ";\n";
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