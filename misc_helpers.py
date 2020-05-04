import shutil
import os

def delete_and_create_folder(f):
    if os.path.isdir(f):
        shutil.rmtree(f)
    os.makedirs(f) # works recursively


def write_debug_file(staffs, folder):
    outstr = ""
    outstr += "\\new GrandStaff   <<\n"
    for s in staffs:
        outstr += "\\new Staff {\n"
        outstr += s.complete_lily_string
        outstr += "\n"
        outstr += "}"
        outstr += "\n"
        outstr += "\n"
        outstr += "\n"
    outstr += ""
    outstr += " >>"
    with open(folder + "/debug.ly", "w") as outfile:
        outfile.write(outstr)


def get_folder_hand_string(options):
    """
    This string will be added to folder names
    to indicate the active hands.
    """
    hand_string = "hands"
    if options["play_left"]:
        hand_string += "_left"
    if options["play_right"]:
        hand_string += "_right"
    return hand_string

def get_true_strings():
    """
    These strings can be used to convert option strings to boolean.
    """
    return ["True", "true", "t", "T", "1"]
