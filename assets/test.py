from vm import *

def main():
    # VM[VM_EVENT] = 1234 < 4567
    # return VM[VM_EVENT]
    if VM[VM_EVENT] == EVENT_KEY_A or VM[VM_EVENT] == EVENT_KEY_START:
        match VM[VM_SELECT_NO]:
            case 0:
                return 0  # START
            case 1:
                return 1  # CONTINUE
            case _:
                return -1  # INVALID SELECTION

