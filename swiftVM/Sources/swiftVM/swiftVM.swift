// The Swift Programming Language
// https://docs.swift.org/swift-book

import swiftVMLib

@main
struct swiftVM {
    static func main() {

        // 1. 仮実行用に、Swiftの管理下でメモリ領域（配列）を確保する
        var rawMem = [UInt16](repeating: 0, count: 256)
        let rawCode = [UInt8](repeating: 0, count: 256)  // 適当なバイトコードの初期値

        var vm = rawMem.withUnsafeMutableBufferPointer { memBuf in
            return rawCode.withUnsafeBufferPointer { codeBuf in
                let memAddr = UInt(UInt(bitPattern: memBuf.baseAddress))
                let codeAddr = UInt(UInt(bitPattern: codeBuf.baseAddress))

                return swiftVMLib(codeAddress: codeAddr, memAddress: memAddr)
            }
        }

        while true {
            let shouldHalt = vm.step()
            if shouldHalt {
                print("HALT(pc:\(vm.getPC())) return:\(vm.result())")
                break
            }
        }
    }
}
