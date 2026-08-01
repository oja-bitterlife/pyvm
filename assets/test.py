from vm import *

def main():
    for VM[VM_FREE] in [1, 3, 5, 7]:
        VM[VM_SELECT_NO] += VM[VM_FREE]
    return VM[VM_SELECT_NO]

    # VM[VM_EVENT] = EVENT_KEY_START
    # VM[VM_SELECT_NO] = 2
    # if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
    #     match VM[VM_SELECT_NO]:
    #         case 0:
    #             return 0  # START
    #         case 1:
    #             return 1  # CONTINUE
    #         case _:
    #             return -1  # INVALID SELECTION

