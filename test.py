from compiler.pyvm_bc import BytecodeCompiler
import argparse

# コマンドライン
# *****************************************************************************
# ファイル名入力
arg_parser = argparse.ArgumentParser(description="Compile Python code to stack-machine bytecode.")
arg_parser.add_argument("input_file", help="Path to the input Python file.")
args = arg_parser.parse_args()

with open(args.input_file, "r") as f:
    bc = BytecodeCompiler(f.read())
    bc.print_bytecode()
