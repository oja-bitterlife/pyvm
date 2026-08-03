from assets.vm import *

value = 0
VM_TEST_RESULT = VM_FREE + 1


def main():
    # テストの結果格納
    VM[VM_TEST_RESULT] = 0  # 成功は 0、失敗したチェック番号を入れる

    VM[VM_EVENT] = EVENT_KEY_START
    VM[VM_SELECT_NO] = 2

    VM[VM_FREE] = 0
    while VM[VM_FREE] < 3:
        VM[VM_FREE] = VM[VM_FREE] + 1

    VM[VM_FREE] = -VM[VM_FREE]
    VM[VM_FREE] += 2

    # ビット演算のテスト
    VM[VM_FREE] = ((VM[VM_FREE] & 2) | 3) ^ 1
    if VM[VM_FREE] != 2:
        VM[VM_TEST_RESULT] = 1

    # +,-のテスト
    VM[VM_FREE] = (VM[VM_FREE] + 2) - 1
    if VM[VM_FREE] != 3:
        VM[VM_TEST_RESULT] = 2

    # *,/のテスト
    VM[VM_FREE] = (VM[VM_FREE] * 3) / 2
    if VM[VM_FREE] != 4:
        VM[VM_TEST_RESULT] = 3

    # %のテスト
    VM[VM_FREE] = (VM[VM_FREE] % 2) + 5
    if VM[VM_FREE] != 5 and VM[VM_FREE] != 6:
        VM[VM_TEST_RESULT] = 4

    # for文のテスト
    VM[VM_FREE] = 0
    for VM[VM_FREE] in [1, 2, 3]:
        VM[VM_FREE] = VM[VM_FREE] + 1
    if VM[VM_FREE] != 4:
        VM[VM_TEST_RESULT] = 8

    if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
        if 1 < 2 < 3 < 4:
            match VM[VM_SELECT_NO]:
                case 2 | 3:
                    if 1 == 1 and 2 != 3 and 1 < 2 and 1 <= 2 and 2 > 1 and 2 >= 2:
                        VM[VM_FREE] = 7
                    else:
                        VM[VM_TEST_RESULT] = 5
                case value:
                    VM[VM_TEST_RESULT] = 6
                    VM[VM_FREE] = value

    if VM[VM_FREE] != 7:
        VM[VM_TEST_RESULT] = 7

    return VM[VM_TEST_RESULT]
