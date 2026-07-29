public struct swiftVMLib {

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
    public var mem: WorkMemory  // 書き換えが必要なら var

    // MARK: - 初期化
    public init(codeAddress: UInt, memAddress: UInt) {
        self.code = CodeMemory(address: codeAddress)
        self.mem = WorkMemory(address: memAddress)
    }
}
