// The Swift Programming Language
// https://docs.swift.org/swift-book

import swiftVMLib

@main
struct swiftVM {
    // 仮想マシンの実行ロジックをここに実装する予定
    // 例えば、命令セットの定義、命令のデコード、実行ループなど
    static func main() {

        // 1. 仮実行用に、Swiftの管理下でメモリ領域（配列）を確保する
        var rawMem = [UInt16](repeating: 0, count: 256)
        let rawCode = [UInt8](repeating: 0, count: 256)  // 適当なバイトコードの初期値

        // 2. 配列の先頭ポインタ（UInt32のアドレス）を取得して swiftVMLib を初期化する
        // Swiftの配列からポインタを取り出すお馴染みの書き方です
        var vm = rawMem.withUnsafeMutableBufferPointer { memBuf in
            return rawCode.withUnsafeBufferPointer { codeBuf in
                let memAddr = UInt(UInt(bitPattern: memBuf.baseAddress))
                let codeAddr = UInt(UInt(bitPattern: codeBuf.baseAddress))

                return swiftVMLib(codeAddress: codeAddr, memAddress: memAddr)
            }
        }

        // 3. 動作テスト
        print("初期状態 mem[0]: \(vm.mem[0])")

        // 書き込みテスト
        vm.mem[0] = 12345
        print("書き込み後 vm.mem[0]: \(vm.mem[0])")

        // Swift側（rawMem）から直接見ても値が変わっているか確認
        print("Swift側 rawMem[0]: \(rawMem[0])")  // 12345 になっているはず！
    }
}
