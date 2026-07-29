// The Swift Programming Language
// https://docs.swift.org/swift-book
import Foundation
import swiftVMLib

let filePath = "../assets/test.bin"

@main
struct swiftVM {
    static func main() {

        // 1. 仮実行用に、Swiftの管理下でメモリ領域（配列）を確保する
        var rawMem = [UInt16](repeating: 0, count: 256)
        //        let rawCode = [UInt8](repeating: 0, count: 256)  // 適当なバイトコードの初期値
        // 2. バイトコードをファイルから読み込む
        let rawCode: [UInt8]
        do {
            rawCode = try Data(contentsOf: URL(fileURLWithPath: filePath)).map { $0 }
        } catch {
            print("Error reading file: \(error)")
            return
        }

        let memAddr = UInt(
            UInt(bitPattern: rawMem.withUnsafeMutableBufferPointer { $0.baseAddress }))
        let codeAddr = UInt(UInt(bitPattern: rawCode.withUnsafeBufferPointer { $0.baseAddress }))
        var vm = swiftVMLib(codeAddress: codeAddr, memAddress: memAddr, memSize: rawMem.count)

        while true {
            let shouldHalt = vm.step()
            if shouldHalt {
                print("HALT(pc:\(vm.getPC())) return:\(vm.result())")
                break
            }
        }
    }
}
