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
        return Int(self.mem[0])
    }
    public func getPC() -> Int {
        return self.pc
    }

    public mutating func step() -> Bool {
        let op = Int(self.code[self.pc])
        self.pc += 1

        switch op {
        case OP_HALT:
            self.pc -= 1  // HALT命令の後はPCを戻す(HALTはpcを進めない)
            return true
        case OP_LDC:
            LDC()
        case OP_LD:
            LD()
        case OP_ST:
            ST()
        case OP_STA:
            STA()
        case OP_JMP:
            assert(
                self.pc == self.code[self.pc],
                "Jump address must be equal to the current program counter")
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

        default:
            assert(false, "Unknown opcode(pc:\(self.pc-1)): \(op)")
        }

        assert(self.pc < 256, "Program counter out of bounds")
        return false
    }

    public mutating func LDC() {
        // LDC命令の実装
        let lower = self.code[self.pc]
        self.pc += 1
        let upper = self.code[self.pc]
        self.pc += 1
        let value = UInt16(upper) << 8 | UInt16(lower)
        self.mem[0] = value
        print("LDC R0 = \(value)")
    }

    public mutating func LD() {
        // LD命令の実装
        let addr = self.code[self.pc]
        self.pc += 1
        self.mem[0] = self.mem[Int(addr)]
        print("LD R0 = VM[\(addr)](\(self.mem[Int(addr)]))")
    }
    public mutating func ST() {
        // ST命令の実装
        let addr = self.code[self.pc]
        self.pc += 1
        self.mem[Int(addr)] = self.mem[0]
        print("ST VM[\(addr)] = R0(\(self.mem[0]))")
    }
    public mutating func STA() {
        // STA命令の実装
        let index = Int(self.code[self.pc])
        self.pc += 1
        let addr = self.mem[index]  // R1に格納されたアドレスを取得
        self.mem[Int(addr)] = self.mem[0]
        print("STA VM[VM[\(addr)]] = R0(\(self.mem[0]))")
    }

    public mutating func JZ() {
        // JZ命令の実装
        let addr = self.code[self.pc]
        self.pc += 1
        if self.mem[0] == 0 {
            self.pc = Int(addr)
        }
        print("JZ: R0 == 0, jumping to \(addr)")
    }
    public mutating func JNZ() {
        // JNZ命令の実装
        let addr = self.code[self.pc]
        self.pc += 1
        if self.mem[0] != 0 {
            self.pc = Int(addr)
        }
        print("JNZ: R0 != 0, jumping to \(addr)")
    }

    public mutating func CMP() {
        let subcode = Int(self.code[self.pc])
        self.pc += 1

        switch subcode {
        case CMP_EQ:
            self.mem[0] = (self.mem[0] == self.mem[1]) ? 1 : 0
        case CMP_NE:
            self.mem[0] = (self.mem[0] != self.mem[1]) ? 1 : 0
        case CMP_LT:
            self.mem[0] = (self.mem[0] < self.mem[1]) ? 1 : 0
        case CMP_LE:
            self.mem[0] = (self.mem[0] <= self.mem[1]) ? 1 : 0
        case CMP_GT:
            self.mem[0] = (self.mem[0] > self.mem[1]) ? 1 : 0
        case CMP_GE:
            self.mem[0] = (self.mem[0] >= self.mem[1]) ? 1 : 0
        default:
            assert(false, "Unknown comparison subcode: \(subcode)")
        }

        print("CMP R0 = \(self.mem[0]) (comparison result)")
    }

    public mutating func NOT() {
        self.mem[0] = (self.mem[0] != 0) ? 1 : 0
    }
    public mutating func ADD() {
        self.mem[0] = self.mem[0] &+ self.mem[1]  // Use wrapping addition to handle overflow
    }
    public mutating func SUB() {
        self.mem[0] = self.mem[0] &- self.mem[1]  // Use wrapping subtraction to handle underflow
    }
    public mutating func MUL() {
        self.mem[0] = self.mem[0] &* self.mem[1]  // Use wrapping multiplication to handle overflow
    }
    public mutating func DIV() {
        assert(self.mem[1] != 0, "Division by zero")
        self.mem[0] = self.mem[0] / self.mem[1]
    }
    public mutating func MOD() {
        assert(self.mem[1] != 0, "Modulo by zero")
        self.mem[0] = self.mem[0] % self.mem[1]
    }
}
