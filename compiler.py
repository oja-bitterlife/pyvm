from assets.vm import *
import argparse
import ast

# 例：超簡易8bit VMのオペコード定義
OP_HALT      = 0x00
OP_LDC       = 0x01  # Load (R0) Constant(word)
OP_LD        = 0x02  # Load (R0) from memory
OP_ST        = 0x03  # Store (R0) to memory
OP_STA       = 0x04  # Store (R0) to VM[R1]
OP_SWP       = 0x05  # Swap R0 and VM[addr]
OP_JMP       = 0x10  # Jump
OP_JZ        = 0x11  # Jump if Zero (R0 == 0)
OP_JNZ       = 0x12  # Jump if Not Zero (R0 != 0)
OP_CMP       = 0x20  # R0とR1を比較してR0に 0 or 1 で結果を格納。比較演算はSubコードで指定する。
OP_NOT       = 0x30  # R0 = R0 != 0 ? 1 : 0
OP_ADD       = 0x31  # R0 = R0 + R1
OP_SUB       = 0x32  # R0 = R0 - R1
OP_MUL       = 0x33  # R0 = R0 * R1
OP_DIV       = 0x34  # R0 = R0 / R1
OP_MOD       = 0x35  # R0 = R0 % R1

# 比較演算のサブコード
CMP_EQ       = 0x00  # R0 == R1
CMP_NE       = 0x01  # R0 != R1
CMP_LT       = 0x02  # R0 < R1
CMP_LE       = 0x03  # R0 <= R1
CMP_GT       = 0x04  # R0 > R1
CMP_GE       = 0x05  # R0 >= R1


class BytecodeCompiler(ast.NodeVisitor):
    def __init__(self):
        self.code = bytearray()
        self.has_main = False

    # 定数をロードするヘルパー関数(LDCは2byteの読み込み)
    def LD_CONST_VAL(self, val, reg=VM_R0):
        self.code.append(OP_LDC)
        self.code.append(val & 0xff)  # 下位8bit
        self.code.append((val >> 8) & 0xff)  # 上位8bitも
        if reg is not VM_R0:
            self.code.append(OP_ST)
            self.code.append(reg)  # 指定されたレジスタに保存

    # 未実装エラー
    def generic_visit(self, node):
        if self.has_main:
            raise NotImplementedError(f"Unsupported AST node: {type(node).__name__}")
        # importとかはおまかせ
        super().generic_visit(node)

    # mainから始める
    def visit_FunctionDef(self, node):
        # 関数名が "main" であるかをチェック
        if node.name == "main":
            # main関数がすでに存在する場合はエラーを出す
            if self.has_main:
                raise Exception("Multiple 'main' functions are not allowed.")

            self.has_main = True

            # main関数の中身（文のリスト）を順にコンパイルしていく
            for stmt in node.body:
                self.visit(stmt)

    # def visit_Return(self, node):
    #     if node.value is None:
    #         self.LD_CONST_VAL(0)  # Noneの場合は0をR0にロード
    #     else:
    #         self.LD_CONST(node.value)  # R0にロード

    #     # Return時にVMを停止させる
    #     self.code.append(OP_HALT)

    # def visit_Constant(self, node):
    #     return int(node.value), False

    # def visit_Name(self, node):
    #     return globals().get(node.id), False

    # # VM[index]のindex部分を返す
    # def visit_Subscript(self, node):
    #     # VM[]以外を却下する
    #     if not isinstance(node.value, ast.Name) or node.value.id != 'VM':
    #         raise NotImplementedError("Only VM[] subscript is supported.")
    #     return self.visit(node.slice), True  # インデックスを返す

    # def visit_Assign(self, node):
    #     # 代入の左辺がVM[]であることを確認
    #     if not isinstance(node.targets[0], ast.Subscript) or not isinstance(node.targets[0].value, ast.Name) or node.targets[0].value.id != 'VM':
    #         raise NotImplementedError("Only assignment to VM[] is supported.")

    #     # 左辺のインデックスを評価してR1にロード
    #     self.LD_CONST(node.targets[0].slice, VM_R1)  # R1にアドレスを保存

    #     # 右辺を評価してR0にロード
    #     self.visit(node.value)


    #     # R0の値をVM[R1]にストア
    #     self.code.append(OP_STA)
    #     self.code.append(VM_R1)  # R1に保存されたアドレスにストア

    # def visit_If(self, node):
    #     # 条件式を評価するコードを生成
    #     self.visit(node.test)
        
    #     # 条件が偽の場合のジャンプ命令 (仮のジャンプ先を空けておく)
    #     self.code.append(OP_JZ)
    #     jump_fixup_pos = len(self.code)
    #     self.code.append(ADDR_ERROR)  # 仮のオフセット

    #     # ifブロック内の処理をコンパイル
    #     for stmt in node.body:
    #         self.visit(stmt)
            
    #     # ジャンプ先（ブロックの終端）のオフセットを計算して代入
    #     target_pos = len(self.code)
    #     self.code[jump_fixup_pos] = min(ADDR_ERROR, target_pos)

    # def visit_Compare(self, node):
    #     self.LD_CONST(node.left, VM_R3)  # R3に保存
        
    #     for op, right in zip(node.ops, node.comparators):
    #         # 右辺を評価
    #         self.LD_CONST(right, VM_R1)  # R1に保存

    #         # 比較する値を引っ張ってくる
    #         self.code.append(OP_LD)
    #         self.code.append(VM_R3)  # R3からR0にロード

    #         # 演算子の種類に応じたサブコードを決定
    #         if isinstance(op, ast.Eq):
    #             cmp_subcode = CMP_EQ
    #         elif isinstance(op, ast.NotEq):
    #             cmp_subcode = CMP_NE
    #         elif isinstance(op, ast.Lt):
    #             cmp_subcode = CMP_LT
    #         elif isinstance(op, ast.LtE):
    #             cmp_subcode = CMP_LE
    #         elif isinstance(op, ast.Gt):
    #             cmp_subcode = CMP_GT
    #         elif isinstance(op, ast.GtE):
    #             cmp_subcode = CMP_GE
    #         # 知らない比較演算子
    #         else:
    #             raise NotImplementedError(f"Unsupported comparison operator: {type(op)}")
            
    #         # OP_CMP命令とサブコードを出力
    #         self.code.append(OP_CMP)
    #         self.code.append(cmp_subcode)

    #         # 右辺(R1)をR3に保存して次の比較に備える
    #         self.code.append(OP_LD)
    #         self.code.append(VM_R1)  # R1からR0にロード
    #         self.code.append(OP_ST)
    #         self.code.append(VM_R3)  # R3に保存

    # def visit_Match(self, node):
    #     # match の対象（subject）を評価
    #     self.LD_CONST(node.subject, VM_R1)  # R1に保存
        
    #     # match 全体を抜けた後のジャンプ先アドレスを保持するリスト
    #     exit_jump_patches = []
        
    #     for case in node.cases:
    #         pattern = case.pattern
            
    #         # ワイルドカード（case _:) の場合
    #         if isinstance(pattern, ast.MatchAs) and pattern.name is None:
    #             # デフォルトケースの処理
    #             for stmt in case.body:
    #                 self.visit(stmt)
    #             break  # デフォルトケースは最後に置くべきなので、ここでループを抜ける
                
    #         # 通常の値マッチングの場合 (例: case 0:, case 1:)
    #         if isinstance(pattern, ast.MatchValue):
    #             # パターンの値を評価
    #             self.LD_CONST(pattern.value)
                
    #             # R1に保存されたmatchの対象と比較
    #             self.code.append(OP_CMP)  # R0 == R1
                
    #             # 条件が偽の場合
    #             self.code.append(OP_JZ)
    #             jump_fixup_pos = len(self.code)
    #             self.code.append(ADDR_ERROR)  # 仮のオフセット
                
    #             # caseブロック内の処理をコンパイル
    #             for stmt in case.body:
    #                 self.visit(stmt)
                
    #             # caseブロックを抜けた後のジャンプ命令 (仮のジャンプ先を空けておく)
    #             self.code.append(OP_JMP)
    #             exit_jump_pos = len(self.code)
    #             self.code.append(ADDR_ERROR)  # 仮のオフセット
    #             exit_jump_patches.append(exit_jump_pos)
                
    #             # ジャンプ先（caseブロックの終端）のオフセットを計算してパッチを当てる
    #             target_pos = len(self.code)
    #             self.code[jump_fixup_pos] = min(ADDR_ERROR, target_pos)

    #     # match全体を抜けた後のジャンプ命令のパッチを当てる
    #     for exit_jump_pos in exit_jump_patches:
    #         self.code[exit_jump_pos] = min(ADDR_ERROR, len(self.code))

    # def visit_For(self, node):
    #     # range(N) の N が定数の場合のみ対応する場合
    #     if isinstance(node.iter, ast.Call) and len(node.iter.args) == 1:
    #         stop_val = node.iter.args[0].value  # 例: 3
            
    #         for i in range(stop_val):
    #             # ループの中身をそのまま愚直に吐き出す！
    #             for stmt in node.body:
    #                 self.visit(stmt)
    #     else:
    #         raise NotImplementedError("Only simple constant range() is supported.")

    # def visit_While(self, node):
    #     # 1. ループの先頭位置を記録
    #     loop_start = len(self.code)
        
    #     # 2. 条件式を評価 (結果が R0 に入る想定)
    #     self.visit(node.test)
        
    #     # 3. 条件が偽 (0) ならループを抜けるジャンプ
    #     self.code.append(OP_JZ)
    #     exit_jump_pos = len(self.code)
    #     self.code.append(ADDR_ERROR)  # 仮のアドレス
        
    #     # 4. ループ本体のコードを生成
    #     for stmt in node.body:
    #         self.visit(stmt)
            
    #     # 5. ループの先頭へ無条件ジャンプ
    #     self.code.append(OP_JMP)
    #     self.code.append(loop_start)
        
    #     # 6. 脱出先アドレスをバックパッチ
    #     target_pos = len(self.code)
    #     self.code[exit_jump_pos] = min(ADDR_ERROR, target_pos)

    # def visit_UnaryOp(self, node):
    #     # マイナスの単項演算子
    #     if isinstance(node.op, ast.USub):
    #         # 定数のマイナス
    #         if isinstance(node.operand, ast.Constant):
    #             self.LD_CONST_VAL(-int(node.operand.value))
    #         # 0から引くことでマイナスを表現する
    #         else:
    #             # オペランド（変数など）を評価してR1に入れる
    #             self.LD_CONST(node.operand, VM_R1)  # R1に保存

    #             # 0 から operand (R1) を引く
    #             self.LD_CONST_VAL(0)  # R0に0をロード
    #             self.code.append(OP_SUB) # R0 = R0 - R1

    #     elif isinstance(node.op, ast.UAdd):
    #         # プラス (+) の処理（中身をそのまま評価するだけでOK）
    #         self.visit(node.operand)
    #     elif isinstance(node.op, ast.Not):
    #         # 否定 (not) の処理（OP_NOT 命令を使うなど）
    #         self.visit(node.operand)
    #         self.code.append(OP_NOT)
    #     else:
    #         raise NotImplementedError(f"Unsupported unary operator: {type(node.op)}")

    # # 二項演算の処理
    # def visit_BinOp(self, node):
    #     self.LD_CONST(node.right, VM_R1)  # R1に保存
    #     self.LD_CONST(node.left)  # R0に保存

    #     # R0 = R0 <op> R1
    #     if isinstance(node.op, ast.Add):
    #         self.code.append(OP_ADD)
    #     elif isinstance(node.op, ast.Sub):
    #         self.code.append(OP_SUB)
    #     elif isinstance(node.op, ast.Mult):
    #         self.code.append(OP_MUL)
    #     elif isinstance(node.op, ast.Div):
    #         self.code.append(OP_DIV)
    #     elif isinstance(node.op, ast.Mod):
    #         self.code.append(OP_MOD)
    #     else:
    #         raise NotImplementedError(f"Unsupported binary operator: {type(node.op)}")

    # def visit_BoolOp(self, node):
    #     # 左辺を評価
    #     left = self.visit(node.values[0])  # 左辺を評価
    #     self.LD_CONST_VAL(left, VM_R3)  # R3に保存

    #     # ループで回すのでチェックは左辺だけでOK。右辺は次のループで左辺になる
    #     for value in node.values[1:]:
    #         self.code.append(OP_LD)
    #         self.code.append(VM_R3)  # R3からR0にロード

    #         if isinstance(node.op, ast.And):
    #             # ANDの場合、左辺が偽なら右辺を評価せずに偽を返す
    #             self.code.append(OP_JZ)
    #             jump_fixup_pos = len(self.code)
    #             self.code.append(ADDR_ERROR)  # 仮のオフセット

    #             self.LD_CONST(value)
                
    #             target_pos = len(self.code)
    #             self.code[jump_fixup_pos] = min(ADDR_ERROR, target_pos)
    #         elif isinstance(node.op, ast.Or):
    #             # ORの場合、左辺が真なら右辺を評価せずに真を返す
    #             self.code.append(OP_JNZ)
    #             jump_fixup_pos = len(self.code)
    #             self.code.append(ADDR_ERROR)  # 仮のオフセット
                
    #             self.LD_CONST(value)
                
    #             target_pos = len(self.code)
    #             self.code[jump_fixup_pos] = min(ADDR_ERROR, target_pos)
    #         else:
    #             raise NotImplementedError(f"Unsupported boolean operator: {type(node.op)}")

    #         # 右辺(R0)をR3に保存して次の比較に備える
    #         self.code.append(OP_ST)
    #         self.code.append(VM_R3)  # R3に保存

# 使用例
arg_parser = argparse.ArgumentParser(description="Compile Python code to bytecode for a simple VM.")
arg_parser.add_argument("input_file", help="Path to the input Python file.")
args = arg_parser.parse_args()

with open(args.input_file, "r") as f:
    tree = ast.parse(f.read())

    compiler = BytecodeCompiler()
    compiler.visit(tree)
    compiler.code.append(OP_HALT)

# Hex出力
binary_data = bytes(compiler.code)
print(" ".join(f"{byte:02X}" for byte in binary_data))
