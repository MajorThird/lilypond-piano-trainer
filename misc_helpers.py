
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
