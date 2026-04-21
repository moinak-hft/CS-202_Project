cmake_minimum_required(VERSION 3.13)
project(CFGProject)

find_package(LLVM REQUIRED CONFIG)
find_package(Clang REQUIRED CONFIG)

include_directories(${LLVM_INCLUDE_DIRS} ${CLANG_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

set(CMAKE_CXX_STANDARD 17)

add_executable(CFGAnalyzer CFGAnalyzer.cpp)

target_link_libraries(CFGAnalyzer
    clangAST
    clangBasic
    clangFrontend
    clangTooling
    clangAnalysis
    LLVMSupport
)