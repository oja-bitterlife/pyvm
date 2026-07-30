from assets.vm import *
import argparse
import ast

# スタックマシン用のオペコード
OP_HALT     = 0x00  # 終了
OP_PUSHA    = 0x01  # スタックにVM[<address>] をプッシュ
OP_PUSHB    = 0x02  # スタックにByteをプッシュ
OP_PUSHW    = 0x03  # スタックにWordをプッシュ
OP_POPA     = 0x04  # スタックからVM[<address>] にポップ
OP_JMP      = 0x10
OP_JZ       = 0x11
OP_JNZ      = 0x12
OP_CMP      = 0x20  # スタックから [左辺, 右辺] をポップして比較し、結果(0 or 1)をプッシュ
OP_AND      = 0x21
OP_OR       = 0x22
OP_XOR      = 0x23
OP_ADD      = 0x30  # スタックから [左辺, 右辺] をポップし、左辺+右辺の結果をプッシュ
OP_SUB      = 0x31
OP_MUL      = 0x32
OP_DIV      = 0x33
OP_MOD      = 0x34

# 比較演算のサブコード
CMP_EQ      = 0x00
CMP_NE      = 0x01
CMP_LT      = 0x02
CMP_LE      = 0x03
CMP_GT      = 0x04
CMP_GE      = 0x05

ADDR_ERROR  = 0xFF


class BytecodeCompiler(ast.NodeVisitor):
    def __init__(self):
        self.code = bytearray()
        self.has_main = False

    def generic_visit(self, node):
        if self.has_main:
            raise NotImplementedError(f"Unsupported AST node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name == "main":
            if self.has_main:
                raise Exception("Multiple 'main' functions are not allowed.")
            self.has_main = True
            for stmt in node.body:
                self.visit(stmt)

    def visit_Return(self, node):
        if node.value is None:
            # 何もなければ0をプッシュして終了
            self.code.append(OP_PUSHB)
            self.code.append(0)
        else:
            self.visit(node.value)

    def visit_Constant(self, node):
        val = int(node.value)
        if(val & 0xFF00) == 0:
            self.code.append(OP_PUSHB)
            self.code.append(val & 0xFF)
        else:
            self.code.append(OP_PUSHW)
            self.code.append(val & 0xFF)
            self.code.append((val >> 8) & 0xFF)

    def visit_Name(self, node):
        val = globals().get(node.id)
        if(val & 0xFF00) == 0:
            self.code.append(OP_PUSHB)
            self.code.append(val & 0xFF)
        else:
            self.code.append(OP_PUSHW)
            self.code.append(val & 0xFF)
            self.code.append((val >> 8) & 0xFF)

    # VM[index] の値をロードしてスタックに積む
    def visit_Subscript(self, node):
        if not isinstance(node.value, ast.Name) or node.value.id != 'VM':
            raise NotImplementedError("Only VM[] subscript is supported.")

        # インデックスを評価してスタックに積む
        self.visit(node.slice)

        # スタックトップのインデックスに対応するメモリ値をロード
        self.code.append(OP_PUSHA)

    # 代入文: VM[<address>] = value
    def visit_Assign(self, node):
        if not isinstance(node.targets[0], ast.Subscript) or not isinstance(node.targets[0].value, ast.Name) or node.targets[0].value.id != 'VM':
            raise NotImplementedError("Only assignment to VM[] is supported.")

        # 右辺の値を先に評価 (スタックに積まれる)
        self.visit(node.value)
        # 左辺のaddressを後から評価 (スタックに積まれる)
        self.visit(node.targets[0].slice)

        # VM[<address>] にポップ
        self.code.append(OP_POPA)

    def visit_BinOp(self, node):
        # 右辺を先に評価 (スタックに積まれる)
        self.visit(node.right)
        # 左辺を後から評価 (スタックに積まれる)
        self.visit(node.left)

        # 演算子に応じたバイトコードを付与
        # （VM側でスタックから [左辺, 右辺] をポップして計算し、結果をプッシュする）
        if isinstance(node.op, ast.BitAnd):
            self.code.append(OP_AND)
        elif isinstance(node.op, ast.BitOr):
            self.code.append(OP_OR)
        elif isinstance(node.op, ast.BitXor):
            self.code.append(OP_XOR)
        elif isinstance(node.op, ast.Add):
            self.code.append(OP_ADD)
        elif isinstance(node.op, ast.Sub):
            self.code.append(OP_SUB)
        elif isinstance(node.op, ast.Mult):
            self.code.append(OP_MUL)
        elif isinstance(node.op, ast.Div):
            self.code.append(OP_DIV)
        elif isinstance(node.op, ast.Mod):
            self.code.append(OP_MOD)
        else:
            raise NotImplementedError(f"Unsupported binary operator: {type(node.op)}")

    # 複数の比較（例: a < b < c）を、(a < b) and (b < c) の ast.BoolOp に分解するヘルパー
    def desugar_compare(self, node):
        if len(node.ops) == 1:
            return node  # 1つだけならそのまま返す

        comparisons = []
        left = node.left

        for op, right in zip(node.ops, node.comparators):
            # 個別の比較式 (left op right) を作る
            comp = ast.Compare(left=left, ops=[op], comparators=[right])
            comparisons.append(comp)
            # 次の比較のために、今の右辺を次の左辺にする
            left = right

        # comparisons が [ (a < b), (b < c) ] になっているので、
        # これを ast.And でつないだ BoolOp にする
        return ast.BoolOp(op=ast.And(), values=comparisons)

    def visit_Compare(self, node):
        # 複数比較が含まれている場合は、and のツリーに変換して再帰的に処理する
        if len(node.ops) > 1:
            desugared_node = self.desugar_compare(node)
            return self.visit(desugared_node)

        # ここから先は「単一の比較 (len(node.ops) == 1)」だけを処理すればOK
        self.visit(node.left)
        self.visit(node.comparators[0])
        
        op = node.ops[0]
        if isinstance(op, ast.Eq): cmp_subcode = CMP_EQ
        elif isinstance(op, ast.NotEq): cmp_subcode = CMP_NE
        elif isinstance(op, ast.Lt): cmp_subcode = CMP_LT
        elif isinstance(op, ast.LtE): cmp_subcode = CMP_LE
        elif isinstance(op, ast.Gt): cmp_subcode = CMP_GT
        elif isinstance(op, ast.GtE): cmp_subcode = CMP_GE
        else: raise NotImplementedError(f"Unsupported operator: {type(op)}")
        
        self.code.append(OP_CMP)
        self.code.append(cmp_subcode)

    def visit_If(self, node):
        self.visit(node.test)
        self.code.append(OP_JZ)
        jump_fixup_pos = len(self.code)
        self.code.append(ADDR_ERROR)

        for stmt in node.body:
            self.visit(stmt)
            
        target_pos = len(self.code)
        self.code[jump_fixup_pos] = min(ADDR_ERROR, target_pos)


# 使用例
arg_parser = argparse.ArgumentParser(description="Compile Python code to stack-machine bytecode.")
arg_parser.add_argument("input_file", help="Path to the input Python file.")
args = arg_parser.parse_args()

with open(args.input_file, "r") as f:
    tree = ast.parse(f.read())
    compiler = BytecodeCompiler()
    compiler.visit(tree)
    compiler.code.append(OP_HALT)

binary_data = bytes(compiler.code)
print(" ".join(f"{byte:02X}" for byte in binary_data))