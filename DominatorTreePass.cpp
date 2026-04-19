#include "llvm/IR/Function.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Dominators.h"

using namespace llvm;

namespace {
struct DominatorTreePass : public PassInfoMixin<DominatorTreePass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        DominatorTree &DT = FAM.getResult<DominatorTreeAnalysis>(F);
        
        errs() << "Dominator Tree for: " << F.getName() << "\n";
        DT.print(errs());
        
        return PreservedAnalyses::all();
    }
};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {LLVM_PLUGIN_API_VERSION, "DominatorTreePass", LLVM_VERSION_STRING,
            [](PassBuilder &PB) {
                PB.registerPipelineParsingCallback(
                    [](StringRef Name, FunctionPassManager &FPM,
                       ArrayRef<PassBuilder::PipelineElement>) {
                        if (Name == "print-dom-tree") {
                            FPM.addPass(DominatorTreePass());
                            return true;
                        }
                        return false;
                    });
            }};
}
