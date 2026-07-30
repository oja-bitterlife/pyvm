from vm import *

def main():
    VM[VM_EVENT] = EVENT_KEY_START
    VM[VM_SELECT_NO] = 2
    if VM[VM_EVENT] == EVENT_KEY_A:
        return 0
    elif VM[VM_EVENT] == EVENT_KEY_START:
        return 1
    else:
        return 2
        # match VM[VM_SELECT_NO]:
        #     case 0:
        #         return 0  # START
        #     case 1:
        #         return 1  # CONTINUE
        #     case _:
        #         return -1  # INVALID SELECTION

