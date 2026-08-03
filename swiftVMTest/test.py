from assets.vm import *

value = 0


def main():
    VM[VM_EVENT] = EVENT_KEY_START
    VM[VM_SELECT_NO] = 2

    VM[VM_FREE] = 0
    while VM[VM_FREE] < 3:
        VM[VM_FREE] = VM[VM_FREE] + 1

    VM[VM_FREE] = -VM[VM_FREE]
    VM[VM_FREE] += 2

    VM[VM_FREE] = ((VM[VM_FREE] & 2) | 3) ^ 1
    VM[VM_FREE] = (VM[VM_FREE] + 2) - 1
    VM[VM_FREE] = (VM[VM_FREE] * 3) / 2
    VM[VM_FREE] = (VM[VM_FREE] % 2) + 5

    if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
        if 1 < 2 < 3 < 4:
            match VM[VM_SELECT_NO]:
                case 2 | 3:
                    if 1 == 1 and 2 != 3 and 1 < 2 and 1 <= 2 and 2 > 1 and 2 >= 2:
                        return VM[VM_FREE]
                    return 0
                case value:
                    return value
        return 0

    if not (VM[VM_FREE] == 0):
        return VM[VM_FREE]

    return 0
