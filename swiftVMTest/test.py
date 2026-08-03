from assets.vm import *


def main():
    VM[VM_EVENT] = EVENT_KEY_START
    VM[VM_SELECT_NO] = 2

    if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
        match VM[VM_SELECT_NO]:
            case 0:
                return 1
            case 1:
                return 2
            case _:
                VM[VM_FREE] = 0
                while VM[VM_FREE] < 3:
                    VM[VM_FREE] = VM[VM_FREE] + 1
                VM[VM_SELECT_NO] = VM[VM_SELECT_NO] + VM[VM_FREE]
                return -1

    VM[VM_FREE] = 0
    for VM[VM_FREE] in [3, 4, EVENT_KEY_B]:
        VM[VM_SELECT_NO] = VM[VM_SELECT_NO] + VM[VM_FREE]

    return VM[VM_SELECT_NO]
