public struct swiftVMLib {
    var pc = 0  // プログラムカウンタ（命令ポインタ）

    // MARK: - コード用メモリ（バイトコード領域）
    public struct CodeMemory {
        private let ptr: UnsafePointer<UInt8>

        fileprivate init(address: UInt) {
            self.ptr = UnsafePointer<UInt8>(bitPattern: address)!
        }

        public subscript(index: Int) -> UInt8 {
            get {
                assert(index >= 0 && index < 256, "Code index out of range")
                return ptr[index]
            }
        }
    }

    // MARK: - ワーク用メモリ（RAM領域）
    public struct WorkMemory {
        private let ptr: UnsafeMutablePointer<UInt16>

        fileprivate init(address: UInt) {
            self.ptr = UnsafeMutablePointer<UInt16>(bitPattern: address)!
            ptr[ADDR_SP] = UInt16(ADDR_STACK)  // スタックポインタの初期化
        }

        public subscript(index: Int) -> UInt16 {
            get {
                assert(index >= 0 && index < 256, "Memory index out of range")
                return ptr[index]
            }
            set {
                assert(index >= 0 && index < 256, "Memory index out of range")
                ptr[index] = newValue
            }
        }

        public mutating func push(value: UInt16) {
            let sp = Int(ptr[ADDR_SP])
            assert(sp > ADDR_SP, "Stack underflow")
            ptr[sp] = value
            ptr[ADDR_SP] = UInt16(sp - 1)
        }

        public mutating func pop() -> UInt16 {
            let sp = Int(ptr[ADDR_SP])
            assert(sp <= ADDR_STACK, "Stack overflow")
            let value = ptr[sp + 1]
            ptr[ADDR_SP] = UInt16(sp + 1)
            return value
        }
    }

    // MARK: - VM本体のプロパティ
    public let code: CodeMemory
    public var mem: WorkMemory

    // MARK: - 初期化
    public init(codeAddress: UInt, memAddress: UInt) {
        self.code = CodeMemory(address: codeAddress)
        self.mem = WorkMemory(address: memAddress)
    }

    public func result() -> Int {
        // メモリ[0] やスタックトップなど、仕様に合わせて調整（例として mem[0] を返す）
        return Int(self.mem[0])
    }

    public func getPC() -> Int {
        return self.pc
    }

    public mutating func step() -> Bool {
        print("PC:\(self.pc)", terminator: " - ")
        let op = Int(self.code[self.pc])
        self.pc += 1

        switch op {
        case OP_HALT:
            self.pc -= 1  // HALT命令の後はPCを戻す
            return true
        case OP_LDC:
            LDC()
        case OP_LD:
            LD()
        case OP_ST:
            ST()
        case OP_JMP:
            self.pc = Int(self.code[self.pc])
        case OP_JZ:
            JZ()
        case OP_JNZ:
            JNZ()
        case OP_CMP:
            CMP()
        case OP_NOT:
            NOT()
        case OP_ADD:
            ADD()
        case OP_SUB:
            SUB()
        case OP_MUL:
            MUL()
        case OP_DIV:
            DIV()
        case OP_MOD:
            MOD()
        case OP_AND:
            AND()
        case OP_OR:
            OR()
        case OP_XOR:
            XOR()

        default:
            assert(false, "Unknown opcode(pc:\(self.pc-1)): \(op)")
        }

        assert(self.pc < 256, "Program counter out of bounds")
        return false
    }

    // MARK: - 命令の実装（スタックマシン版）

    public mutating func LDC() {
        let lower = self.code[self.pc]
        self.pc += 1
        let upper = self.code[self.pc]
        self.pc += 1
        let value = UInt16(upper) << 8 | UInt16(lower)

        // 定数を評価スタックにプッシュ
        self.mem.push(value: value)
        print("LDC pushed \(value)")
    }

    public mutating func LD() {
        // スタックトップからメモリアドレスを取り出し、その番地の値をロードして再びプッシュ
        let addr = self.mem.pop()
        let value = self.mem[Int(addr)]
        self.mem.push(value: value)
        print("LD: loaded VM[\(addr)] = \(value) to stack")
    }

    public mutating func ST() {
        // スタックから [アドレス, 値] の順でポップしてメモリにストア
        // ※コンパイラの生成順序（値 -> アドレス の順で積む想定）に合わせてポップ
        let addr = self.mem.pop()
        let value = self.mem.pop()
        self.mem[Int(addr)] = value
        print("ST: VM[\(addr)] = \(value)")
    }

    public mutating func JZ() {
        let addr = self.code[self.pc]
        self.pc += 1
        // 条件値はスタックからポップして判定
        let cond = self.mem.pop()
        if cond == 0 {
            self.pc = Int(addr)
        }
        print("JZ: condition == 0, jumping to \(addr)")
    }

    public mutating func JNZ() {
        let addr = self.code[self.pc]
        self.pc += 1
        let cond = self.mem.pop()
        if cond != 0 {
            self.pc = Int(addr)
        }
        print("JNZ: condition != 0, jumping to \(addr)")
    }

    public mutating func CMP() {
        let subcode = Int(self.code[self.pc])
        self.pc += 1

        // スタックから右辺、左辺の順にポップする（LIFOなので後から積んだ右辺が先に出る）
        let right = self.mem.pop()
        let left = self.mem.pop()

        let result: UInt16
        switch subcode {
        case CMP_EQ: result = (left == right) ? 1 : 0
        case CMP_NE: result = (left != right) ? 1 : 0
        case CMP_LT: result = (left < right) ? 1 : 0
        case CMP_LE: result = (left <= right) ? 1 : 0
        case CMP_GT: result = (left > right) ? 1 : 0
        case CMP_GE: result = (left >= right) ? 1 : 0
        default:
            assert(false, "Unknown comparison subcode: \(subcode)")
            result = 0
        }

        // 比較結果をスタックにプッシュ
        self.mem.push(value: result)
        print("CMP result \(result) pushed to stack")
    }

    public mutating func NOT() {
        let val = self.mem.pop()
        let result: UInt16 = (val != 0) ? 0 : 1
        self.mem.push(value: result)
        print("NOT: !\(val) = \(result)")
    }

    public mutating func ADD() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left &+ right
        self.mem.push(value: result)
        print("ADD: \(left) + \(right) = \(result)")
    }

    public mutating func SUB() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left &- right
        self.mem.push(value: result)
        print("SUB: \(left) - \(right) = \(result)")
    }

    public mutating func MUL() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left &* right
        self.mem.push(value: result)
        print("MUL: \(left) * \(right) = \(result)")
    }

    public mutating func DIV() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        assert(right != 0, "Division by zero")
        let result = left / right
        self.mem.push(value: result)
        print("DIV: \(left) / \(right) = \(result)")
    }

    public mutating func MOD() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        assert(right != 0, "Modulo by zero")
        let result = left % right
        self.mem.push(value: result)
        print("MOD: \(left) % \(right) = \(result)")
    }

    public mutating func AND() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left & right
        self.mem.push(value: result)
        print("AND: \(left) & \(right) = \(result)")
    }

    public mutating func OR() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left | right
        self.mem.push(value: result)
        print("OR: \(left) | \(right) = \(result)")
    }

    public mutating func XOR() {
        let right = self.mem.pop()
        let left = self.mem.pop()
        let result = left ^ right
        self.mem.push(value: result)
        print("XOR: \(left) ^ \(right) = \(result)")
    }
}
