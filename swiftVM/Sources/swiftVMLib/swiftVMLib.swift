// swiftVMLib.swift

/// デバッグビルド時のみコンパイル・実行されるprint関数
@inlinable
@inline(__always)
public func dprint(_ items: Any..., separator: String = " ", terminator: String = "\n") {
    #if DEBUG
        let output = items.map { "\($0)" }.joined(separator: separator)
        Swift.print(output, terminator: terminator)
    #endif
}

// ============================================================================
// MARK: VM本体
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
        private let size: Int

        fileprivate init(address: UInt, size: Int) {
            self.ptr = UnsafeMutablePointer<UInt16>(bitPattern: address)!
            self.size = size
        }

        public subscript(index: Int) -> UInt16 {
            get {
                assert(index >= 0 && index < self.size, "Memory index out of range")
                return ptr[index]
            }
            set {
                assert(index >= 0 && index < self.size, "Memory index out of range")
                ptr[index] = newValue
            }
        }
    }

    // MARK: - スタック操作
    public struct StackMemory {
        private let ptr: UnsafeMutablePointer<UInt16>
        private let size: Int
        private var sp: Int
        #if DEBUG
            public var stackMax: Int = 0  // スタックの最大使用量を追跡するためのデバッグ用変数
        #endif

        fileprivate init(address: UInt, size: Int) {
            self.ptr = UnsafeMutablePointer<UInt16>(bitPattern: address)!
            self.size = size
            self.sp = 0
        }

        public mutating func push(value: UInt16) {
            assert(self.sp < self.size, "Stack overflow")
            self.ptr[self.sp] = value
            self.sp += 1
            #if DEBUG
                if self.sp > self.stackMax {
                    self.stackMax = self.sp
                }
            #endif
        }
        public mutating func pop() -> UInt16 {
            assert(self.sp > 0, "Stack underflow")
            self.sp -= 1
            return self.ptr[self.sp]
        }

        public func peek() -> UInt16 {
            assert(self.sp > 0, "Stack is empty")
            return self.ptr[self.sp - 1]
        }
    }

    /// デバッグビルド時のみOPコードの実行をトレースする関数
    @inline(__always)
    public func op_trace(_ items: Any..., separator: String = " ", terminator: String = "\n") {
        #if DEBUG
            let output = items.map { "\($0)" }.joined(separator: separator)
            Swift.print(output, terminator: terminator)
        #endif
    }

    // MARK: - VM本体のプロパティ
    public let code: CodeMemory
    public var mem: WorkMemory
    public var stack: StackMemory

    // MARK: - 初期化
    public init(
        codeAddress: UInt,
        stackAddress: UInt, stackSize: Int,
        memAddress: UInt, memSize: Int
    ) {
        self.code = CodeMemory(address: codeAddress)
        self.mem = WorkMemory(address: memAddress, size: memSize)
        self.stack = StackMemory(address: stackAddress, size: stackSize)
    }

    public func result() -> Int {
        return Int(self.stack.peek())
    }

    public func getPC() -> Int {
        return Int(self.pc)
    }

    public mutating func step() -> Bool {
        let op = Int(self.code[self.pc])
        self.op_trace("\(self.pc):", terminator: " ")
        self.pc += 1

        switch op {
        case OP_HALT:
            self.HALT()
            return true
        case OP_PUSHA:
            self.PUSHA()
        case OP_PUSHB:
            self.PUSHB()
        case OP_PUSHW:
            self.PUSHW()
        case OP_POPA:
            self.POPA()
        case OP_DUP:
            self.DUP()
        case OP_DEL:
            self.DEL()
        case OP_JMP:
            self.JMP()
        case OP_JZ:
            self.JZ()
        case OP_CMP:
            self.CMP()
        case OP_AND:
            self.AND()
        case OP_OR:
            self.OR()
        case OP_XOR:
            self.XOR()
        case OP_NOT:
            self.NOT()
        case OP_ADD:
            self.ADD()
        case OP_SUB:
            self.SUB()
        case OP_MUL:
            self.MUL()
        case OP_DIV:
            self.DIV()
        case OP_MOD:
            self.MOD()
        default:
            assert(false, "Unknown opcode(pc:\(self.pc-1)): \(op)")
        }

        assert(self.pc < 256, "Program counter out of bounds")
        return false
    }

    // MARK: - 命令の実装（スタックマシン版）

    @inline(__always)
    public mutating func HALT() {
        self.pc -= 1  // HALT命令の後はPCを戻す
        self.op_trace("HALT")
    }

    @inline(__always)
    public mutating func PUSHA() {
        let addr = self.stack.pop()
        self.stack.push(value: self.mem[Int(addr)])
        self.op_trace("PUSHA \(self.mem[Int(addr)]) in VM[\(Int(addr))]")
    }
    @inline(__always)
    public mutating func PUSHB() {
        let value = self.code[self.pc]
        self.pc += 1
        self.stack.push(value: UInt16(value))
        self.op_trace("PUSHB \(value)")
    }
    @inline(__always)
    public mutating func PUSHW() {
        let value = UInt16(self.code[self.pc + 1]) << 8 | UInt16(self.code[self.pc])
        self.pc += 2
        self.stack.push(value: value)
        self.op_trace("PUSHW \(value)")
    }
    @inline(__always)
    public mutating func POPA() {
        let addr = self.stack.pop()
        let value = self.stack.pop()
        self.mem[Int(addr)] = value
        self.op_trace("POPA VM[\(Int(addr))] <= \(value)")
    }
    @inline(__always)
    public mutating func DUP() {
        let value = self.stack.peek()
        self.stack.push(value: value)
        self.op_trace("DUP \(value)")
    }
    @inline(__always)
    public mutating func DEL() {
        let value = self.stack.pop()
        self.op_trace("DEL \(value)")
    }

    @inline(__always)
    public mutating func JMP() {
        self.pc = Int(self.code[self.pc])
        self.op_trace("JMP to \(self.pc)")
    }
    @inline(__always)
    public mutating func JZ() {
        let addr = self.code[self.pc]
        self.pc += 1
        // 条件値はスタックからポップして判定
        let cond = self.stack.pop()
        if cond == 0 {
            self.op_trace("JZ \(cond): jump to \(addr)")
            self.pc = Int(addr)
        } else {
            self.op_trace("JZ \(cond): pass")
        }
    }
    @inline(__always)
    public mutating func NOT() {
        let value = self.stack.pop()
        let result: UInt16 = (value == 0) ? 1 : 0
        self.stack.push(value: result)
        self.op_trace("NOT \(value) => \(result)")
    }

    @inline(__always)
    public mutating func CMP() {
        let subcode = Int(self.code[self.pc])
        self.pc += 1

        // スタックから右辺、左辺の順にポップする（LIFOなので後から積んだ右辺が先に出る）
        let right = self.stack.pop()
        let left = self.stack.pop()

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
        self.stack.push(value: result)

        #if DEBUG
            let subcodes = ["==", "!=", "<", "<=", ">", ">="]
            self.op_trace("CMP \(left) \(subcodes[subcode]) \(right) => \(result)")
        #endif
    }

    @inline(__always)
    public mutating func AND() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left & right
        self.stack.push(value: result)
        self.op_trace("AND \(left) & \(right) => \(result)")
    }
    @inline(__always)
    public mutating func OR() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left | right
        self.stack.push(value: result)
        self.op_trace("OR \(left) | \(right) => \(result)")
    }
    @inline(__always)
    public mutating func XOR() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left ^ right
        self.stack.push(value: result)
        self.op_trace("XOR \(left) ^ \(right) => \(result)")
    }

    @inline(__always)
    public mutating func ADD() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left &+ right
        self.stack.push(value: result)
        self.op_trace("ADD \(left) + \(right) => \(result)")
    }
    @inline(__always)
    public mutating func SUB() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left &- right
        self.stack.push(value: result)
        self.op_trace("SUB \(left) - \(right) => \(result)")
    }
    @inline(__always)
    public mutating func MUL() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        let result = left &* right
        self.stack.push(value: result)
        self.op_trace("MUL \(left) * \(right) => \(result)")
    }
    @inline(__always)
    public mutating func DIV() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        assert(right != 0, "Division by zero")
        let result = left / right
        self.stack.push(value: result)
        self.op_trace("DIV \(left) / \(right) => \(result)")
    }
    @inline(__always)
    public mutating func MOD() {
        let left = self.stack.pop()
        let right = self.stack.pop()
        assert(right != 0, "Modulo by zero")
        let result = left % right
        self.stack.push(value: result)
        self.op_trace("MOD \(left) % \(right) => \(result)")
    }
}
