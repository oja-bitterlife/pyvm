#from assets.vm import *
import ast
import base64

# 例：超簡易8bit VMのオペコード定義
OP_HALT      = 0x00
OP_PUSH_CONST= 0x01
OP_LOAD_VAR  = 0x02
OP_STORE_VAR = 0x03
OP_ADD       = 0x10
OP_SUB       = 0x11
OP_JMP_FALSE = 0x20
OP_JMP       = 0x21

class BytecodeCompiler(ast.NodeVisitor):
    def __init__(self):
        self.code = bytearray()

    def visit_Constant(self, node):
        # 定数をプッシュする命令 (例: OP_PUSH_CONST, value)
        self.code.append(OP_PUSH_CONST)
        self.code.append(int(node.value) & 0xFF)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if isinstance(node.op, ast.Add):
            self.code.append(OP_ADD)
        elif isinstance(node.op, ast.Sub):
            self.code.append(OP_SUB)

    # 必要に応じて if, for, Assign などを追加していく...

# 使用例
with open("assets/test.py", "r") as f:
    tree = ast.parse(f.read())

    compiler = BytecodeCompiler()
    compiler.visit(tree)
    compiler.code.append(OP_HALT)

# Hex出力
binary_data = bytes(compiler.code)

hex_space = " ".join(f"{b:02X}" for b in binary_data)

print(f"Binary length: {len(binary_data)} bytes")
print(f"Hex (Space) : {hex_space}")
