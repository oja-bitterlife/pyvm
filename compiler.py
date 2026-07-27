from assets.vm import *
import ast
import base64

# 例：超簡易8bit VMのオペコード定義
OP_HALT      = 0x00
OP_LD       = 0x01  # Load from memory
OP_ST       = 0x02  # Store to memory
OP_LDC       = 0x03  # Load (R0) Constant
OP_JMP       = 0x10
OP_JZ        = 0x11
OP_JNZ        = 0x12
OP_CMP       = 0x20
OP_ADD       = 0x30
OP_SUB       = 0x31

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
        self.code.append(OP_JZ)
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
        self.code.append(int(node.value) & 0xff)  # 8bitに収める

    def visit_Name(self, node):
        val = globals().get(node.id)
        if val is not None:
            self.code.append(int(val) & 0xff)  # 8bitに収める
        else:
            raise NameError(f"Name '{node.id}' is not defined in compiler context.")

    def visit_Subscript(self, node):
        self.code.append(OP_LD)
        self.visit(node.slice)

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

    def visit_Match(self, node):
        # 1. match の対象（subject）を評価してスタックに積む
        self.visit(node.subject)
        
        # match 全体を抜けた後のジャンプ先アドレスを保持するリスト
        exit_jump_patches = []
        
        for case in node.cases:
            pattern = case.pattern
            
            # ワイルドカード（case _:) の場合
            if isinstance(pattern, ast.MatchAs) and pattern.name is None:
                # 無条件でここに入る（デフォルトケース）
                for stmt in case.body:
                    self.visit(stmt)
                continue
                
            # 通常の値マッチングの場合 (例: case 0:, case 1:)
            if isinstance(pattern, ast.MatchValue):
                # パターンの値を評価してスタックに積む
                self.visit(pattern.value)
                
                # スタック上の2つの値を比較する命令を出力
                self.code.append(OP_CMP)
                self.code.append(0x00)  # CMP_EQ
                
                # 条件が偽の場合のジャンプ命令 (仮のジャンプ先を空けておく)
                self.code.append(OP_JMP_FALSE)
                jump_fixup_pos = len(self.code)
                self.code.append(0xff)  # 仮のオフセット
                
                # caseブロック内の処理をコンパイル
                for stmt in case.body:
                    self.visit(stmt)
                
                # caseブロックを抜けた後のジャンプ命令 (仮のジャンプ先を空けておく)
                self.code.append(OP_JMP)
                exit_jump_pos = len(self.code)
                self.code.append(0xff)  # 仮のオフセット
                exit_jump_patches.append(exit_jump_pos)
                
                # ジャンプ先（caseブロックの終端）のオフセットを計算してパッチを当てる
                target_pos = len(self.code)
                self.code[jump_fixup_pos] = min(0xff, target_pos)

        # match全体を抜けた後のジャンプ命令のパッチを当てる
        for exit_jump_pos in exit_jump_patches:
            self.code[exit_jump_pos] = min(0xff, len(self.code))


    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if isinstance(node.op, ast.Add):
            self.code.append(OP_ADD)
        elif isinstance(node.op, ast.Sub):
            self.code.append(OP_SUB)

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
