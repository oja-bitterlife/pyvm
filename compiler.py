from assets.vm import *
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
OP_CMP       = 0x30

class BytecodeCompiler(ast.NodeVisitor):
    def __init__(self):
        self.code = bytearray()
        self.has_main = False

    def visit_FunctionDef(self, node):
        print(f"Compiling function: {node.name}")

        # 関数名が "main" であるかをチェック
        if node.name == "main":
            # main関数がすでに存在する場合はエラーを出す
            if self.has_main:
                raise Exception("Multiple 'main' functions are not allowed.")

            self.has_main = True

            # main関数の中身（文のリスト）を順にコンパイルしていく
            for stmt in node.body:
                self.visit(stmt)

    def visit_If(self, node):
        # 1. 条件式を評価するコードを生成
        self.visit(node.test)
        
        # 2. 条件が偽の場合のジャンプ命令 (仮のジャンプ先を空けておく)
        self.code.append(OP_JMP_FALSE)
        jump_fixup_pos = len(self.code)
        self.code.append(0xff)  # 仮のオフセット

        # 3. ifブロック内の処理をコンパイル
        for stmt in node.body:
            self.visit(stmt)
            
        # 4. ジャンプ先（ブロックの終端）のオフセットを計算してパッチを当てる
        # （ここでは8bitの相対ジャンプや絶対アドレスとして書き戻す）
        target_pos = len(self.code)
        self.code[jump_fixup_pos] = min(0xff, target_pos)

    def visit_Constant(self, node):
        self.code.append(OP_PUSH_CONST)
        self.code.append(node.value)

    def visit_Name(self, node):
        val = globals().get(node.id)
        if val is not None:
            self.code.append(OP_PUSH_CONST)
            self.code.append(int(val) & 0xFF)
        else:
            raise NameError(f"Name '{node.id}' is not defined in compiler context.")

    def visit_Subscript(self, node):
        # 例: VM[REG_EVENT] の中身（REG_EVENTの部分 = node.slice）を評価してスタックに積む
        self.visit(node.slice)
        # そのアドレスから値をロードする命令を積む
        self.code.append(OP_LOAD_VAR)

    def visit_Compare(self, node):
        # 左辺を評価 (スタックに積まれる)
        self.visit(node.left)
        
        # 右辺を評価 (スタックに積まれる)
        # ※通常は1つの演算子を想定
        for op, right in zip(node.ops, node.comparators):
            self.visit(right)
            
            # 演算子の種類に応じたサブコードを決定
            if isinstance(op, ast.Eq):
                cmp_subcode = 0x00  # CMP_EQ
            elif isinstance(op, ast.NotEq):
                cmp_subcode = 0x01  # CMP_NE
            elif isinstance(op, ast.Lt):
                cmp_subcode = 0x02  # CMP_LT
            elif isinstance(op, ast.LtE):
                cmp_subcode = 0x03  # CMP_LE
            elif isinstance(op, ast.Gt):
                cmp_subcode = 0x04  # CMP_GT
            elif isinstance(op, ast.GtE):
                cmp_subcode = 0x05  # CMP_GE
            # 必要に応じて他の演算子も追加...
            else:
                raise NotImplementedError(f"Unsupported comparison operator: {type(op)}")
            
            # OP_CMP命令とサブコードを出力
            self.code.append(OP_CMP)
            self.code.append(cmp_subcode)


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
