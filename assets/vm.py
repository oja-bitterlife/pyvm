# メモリ
VM = [0] * 256

# アドレス定義
# *********************************************************
# エラー終了時のアドレス
ADDR_ERROR = 0xFF


# メモリ定義
# *********************************************************
# 4つの汎用レジスタを定義
VM_R0 = 0  # アキュムレータ
VM_R1 = 1  # ２項演算用
VM_R2 = 2  # ループカウンタ
VM_R3 = 3  # 一時的な値

# 追加のレジスタを定義
VM_EVENT = 4
VM_SELECT_NO = 5

# 以下自由に
VM_FREE = 16


# イベント定義
# *********************************************************
# システム固定イベントコード
EVENT_KEY = 0x10
EVENT_KEY_START = EVENT_KEY | 1
EVENT_KEY_SELECT = EVENT_KEY | 2
EVENT_KEY_A = EVENT_KEY | 3
EVENT_KEY_B = EVENT_KEY | 4
EVENT_KEY_LEFT = EVENT_KEY | 5
EVENT_KEY_RIGHT = EVENT_KEY | 6
EVENT_KEY_UP = EVENT_KEY | 7
EVENT_KEY_DOWN = EVENT_KEY | 8
