# GET AB CONFIG FILE
import os
import sys
from config import TARGET_SLOT

# UPDATE CONFIG FILE FUNCTION
def updateAB(fileName, originalText, newText):
    with open(fileName, "r") as f:
        filedata = f.read()

    newdata = filedata.replace(originalText, newText)

    with open(fileName, "w") as f:
        f.write(newdata)


def getNewSlot():
    # OUTPUT AND ASK QUESTION
    print(f"++++++++\nCurrent TARGET_SLOT: \n{TARGET_SLOT}\n++++++++\n")
    while 1:
        try:
            take_in = input("Enter new SLOT TARGET: ")
            NEWSLOT = int(take_in)
            break
        except ValueError as e:
            print(f"Please Enter an Integer! Message [ {e} ]")
    return NEWSLOT


def restartSession() -> None:
    os.system("tmux kill-ses -t autobidder")
    os.system(
        "tmux new-session -s autobidder 'python3 ~/harmony_autobidder/autobid.py'"
    )
    # os.system("tmux ls")


def editAutobidder(TARGET_SLOT: int, configPath: str) -> None:
    # EDIT AUTOBIDDER CONFIG FILE
    # Get New Slot
    NEWSLOT = sys.argv[1] if len(sys.argv) > 1 else getNewSlot()
    ORIG_TARGET = f"TARGET_SLOT = {TARGET_SLOT}"
    NEW_TARGET = f"TARGET_SLOT = {NEWSLOT}"
    updateAB(configPath, ORIG_TARGET, NEW_TARGET)
    print(f"++++++++\nTarget slot updated to {NEWSLOT}\n++++++++")


if __name__ == "__main__":
    config_path = "../harmony_autobidder/config.py"
    editAutobidder(TARGET_SLOT, config_path)
    restartSession()
