from assets.vm import *

test = {
    "VM_TEST": VM_FREE+1,
}

a = test["VM_TEST"]
b = [i*2+1 for i in range(4)]

def main():
    for VM[VM_FREE] in b:
        VM[a] += VM[VM_FREE]
    return VM[a]

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

