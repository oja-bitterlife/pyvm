// The Swift Programming Language
// https://docs.swift.org/swift-book
import Foundation
import swiftVMLib

let filePath = "../assets/test.bin"

@main
struct swiftVM {
    static func main() {
        // メモリ確保
        let rawCode: [UInt8]
        do {
            rawCode = try Data(contentsOf: URL(fileURLWithPath: filePath)).map { $0 }
        } catch {
            print("Error reading file: \(error)")
            return
        }
        var rawMem = [UInt16](repeating: 0, count: 256)
        var stackMem = [UInt16](repeating: 0, count: 256)

        // メモリアドレスの取得
        let codeAddr = UInt(UInt(bitPattern: rawCode.withUnsafeBufferPointer { $0.baseAddress }))
        let memAddr = UInt(
            UInt(bitPattern: rawMem.withUnsafeMutableBufferPointer { $0.baseAddress }))
        let stackAddr = UInt(
            UInt(bitPattern: stackMem.withUnsafeMutableBufferPointer { $0.baseAddress }))

        // VMの初期化
        var vm = swiftVMLib(
            codeAddress: codeAddr,
            stackAddress: stackAddr, stackSize: stackMem.count,
            memAddress: memAddr, memSize: rawMem.count
        )

        while true {
            let shouldHalt = vm.step()
            if shouldHalt {
                print("HALT(pc:\(vm.getPC())) return:\(vm.result())")
                break
            }
        }
    }
}
