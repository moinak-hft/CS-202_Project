cmake_minimum_required(VERSION 3.13.4)
project(CS202_Advanced_Analysis)

# Find LLVM and Clang packages
find_package(LLVM REQUIRED CONFIG)
find_package(Clang REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

# Set include directories
include_directories(${LLVM_INCLUDE_DIRS} ${CLANG_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# Setup compiler flags
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")

# 1. Build the standalone Clang Tool (CFGAnalyzer)
add_executable(CFGAnalyzer llvm_passes/CFGAnalyzer.cpp)
target_link_libraries(CFGAnalyzer
    clangAST
    clangBasic
    clangFrontend
    clangTooling
    clangAnalysis
    LLVMSupport
)

# 2. Build the LLVM Optimizer Pass (Dominator Tree) as a shared library (.so)
add_library(DominatorTreePass MODULE llvm_passes/DominatorTreePass.cpp)
target_link_libraries(DominatorTreePass LLVMSupport LLVMCore LLVMAnalysis)
