# pyvm

Pythonスクリプトを小さな独自バイトコードへ変換し、組み込み向けVMで実行するためのプロジェクトです。

実行系をSwiftで用意しており、GBA向けにビルドすると4.2KB程度になります。

## 目的

- Pythonの一部構文を独自バイトコードへコンパイルする
- 組み込み向けに小さいメモリフットプリントで実行する
- ホスト環境で検証しつつ、最終的に組み込みターゲットへ移植する

## サンプル

組み込みUI向けスクリプトで、決定キーが押された時に選択されているアイテムによってReturnを変化させる

```python
# 定数定義ファイルの読み込み
from assets.vm import *

# mainから開始になります
def main():
    # Test用状態設定
    VM[VM_EVENT] = EVENT_KEY_START
    VM[VM_SELECT_NO] = 2

    if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
        match VM[VM_SELECT_NO]:
            case 0:
                return 0  # START
            case 1:
                return 1  # CONTINUE
            case _:
                return -1  # INVALID SELECTION
```

出力

```bash
$ task data_ck
02 11 02 01 04 02 02 02 02 04 02 01 01 02 13 20 00 02 01 01 02 11 20 00 22 11 3D 02 02 01 05 02 00 20 00 11 2A 02 00 00 10 3C 05 02 01 20 00 11 36 02 01 00 10 3C 02 01 02 00 31 00 08 02 00 00
```

実行

```bash
$ task run
0: PUSHB 17
2: PUSHB 1
4: POPA VM[1] <= 17
5: PUSHB 2
7: PUSHB 2
9: POPA VM[2] <= 2
10: PUSHB 1
12: PUSHA 17 from VM[1]
13: PUSHB 19
15: CMP 17 == 19 => 0
17: PUSHB 1
19: PUSHA 17 from VM[1]
20: PUSHB 17
22: CMP 17 == 17 => 1
24: OR 1 | 0 => 1
25: JZ 1: pass
27: PUSHB 2
29: PUSHA 2 from VM[2]
30: DUP 2
31: PUSHB 0
33: CMP 2 == 0 => 0
35: JZ 0: jump to 42
42: DUP 2
43: PUSHB 1
45: CMP 2 == 1 => 0
47: JZ 0: jump to 54
54: PUSHB 1
56: PUSHB 0
58: SUB 0 - 1 => 65535
59: HALT
return: 65535
Stack max usage: 3 / 64
```

VM[VM_EVENT] が `EVENT_KEY_START` なので ifの中に入り、`VM[VM_SELECT_NO]` が2なので `-1(0xffff)` が返ります

## 構成

- `compiler/pyvm_bc.py`
	- Python ASTを解析し、スタックマシン向けバイトコードを生成
	- 出力は16進文字列（例: `02 01 02 02 30 00`）かbyte列

- `swiftVM/Sources/swiftVMLib/`
	- 組み込み向け実行ライブラリ（Swift）
	- 命令デコーダ、スタック、ワークメモリ、比較/算術/分岐命令を実装

- `swiftVM/Sources/swiftVM/swiftVM.swift`
	- ホスト実行用のサンプルランナー
	- `assets/test.bin` を読み込み、VMをステップ実行

- `assets/`
	- 入力Pythonスクリプトや生成バイトコードなどの検証用

## ローカル開発コマンド

このリポジトリでは `taskfile.yaml` に基本コマンドを定義しています。

- バイトコード確認
	- `task data_ck`
- バイナリ生成（`assets/test.bin`）
	- `task data_mk`
- Swift VM実行
	- `task run`
- Swift VMビルド
	- `task build`

## 組み込み向け

- `-D EMBEDDED` を付けてコンパイルしてください

## 補足

Pythonスクリプトでは、関数や例外は使用できません。

mainの中では変数定義ができません。VM(実機メモリ)を使ってください。

for文は `for VM[???] in [list or tuple]` の形式のみ使えます。iter部分は`list or tuple`であれば変数でもOK。

