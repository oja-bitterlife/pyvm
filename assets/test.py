from vm import *

def main():
    if VM[REG_EVENT] == EVENT_KEY_ENTER:
        match VM[REG_SELECT_NO]:
            case 0:
                return 0  # START
            case 1:
                return 1  # CONTINUE
            case _:
                return -1  # INVALID SELECTION

