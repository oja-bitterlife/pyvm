import Foundation
import swiftVMLib

func resolveBinaryPath() -> String? {
    let cwd = FileManager.default.currentDirectoryPath
    let candidates = [
        "\(cwd)/swiftVMTest/.build/test.bin"
    ]

    for candidate in candidates where FileManager.default.fileExists(atPath: candidate) {
        return candidate
    }
    return nil
}

@main
struct swiftVMTestHarness {
    static func main() {
        guard let filePath = resolveBinaryPath() else {
            print("Could not find assets/test.bin")
            return
        }

        let rawCode: [UInt8]
        do {
            rawCode = try Data(contentsOf: URL(fileURLWithPath: filePath)).map { $0 }
        } catch {
            print("Error reading file: \(error)")
            return
        }

        var rawMem = [UInt16](repeating: 0, count: 64)
        var stackMem = [UInt16](repeating: 0, count: 128)

        let codeAddr = UInt(UInt(bitPattern: rawCode.withUnsafeBufferPointer { $0.baseAddress }))
        let memAddr = UInt(
            UInt(bitPattern: rawMem.withUnsafeMutableBufferPointer { $0.baseAddress }))
        let stackAddr = UInt(
            UInt(bitPattern: stackMem.withUnsafeMutableBufferPointer { $0.baseAddress }))

        var vm = swiftVMLib(
            codeAddress: codeAddr,
            stackAddress: stackAddr,
            stackSize: stackMem.count,
            memAddress: memAddr,
            memSize: rawMem.count
        )

        while true {
            let shouldHalt = vm.step()
            if shouldHalt {
                print("result: \(vm.result())")
                print("stackMax: \(vm.stack.stackMax) / \(stackMem.count)")
                break
            }
        }
    }
}
