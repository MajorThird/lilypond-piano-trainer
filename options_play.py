import argparse
import configparser
import os
import misc_helpers

def get_config(filename):
    """
    All settings are stored in an external text file.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
        required=False,
        default="options.cfg",
        help="path to program options file")
    parser.add_argument("-s", "--song",
        required=False,
        help="use this song instead of the one in the config file")
    parser.add_argument("-r", "--right",
        required=False,
        help="create song for the right hand [possible values: 0,1] ")
    parser.add_argument("-l", "--left",
        required=False,
        help="create song for the left hand [possible values: 0,1] ")
    parser.add_argument("-d", "--device",
        required=False,
        help="number of the MIDI device (use aconnect to find out)")
    parser.add_argument("-p", "--present",
        required=False,
        help="display in presentation mode")
    return parser




def get_options_from_config(config):
    true_strings = misc_helpers.get_true_strings()
    options = {}
    options["song"] = config["PLAY_OPTIONS"]["song"]
    options["play_right"] = True if config["PLAY_OPTIONS"]["play_right"] in true_strings else False
    options["play_left"] = True if config["PLAY_OPTIONS"]["play_left"] in true_strings else False
    options["presentation_mode"] = True if config["PLAY_OPTIONS"]["presentation_mode"] in true_strings else False
    options["songs_folder"] = misc_helpers.normalize_folder_string(config["PLAY_OPTIONS"]["songs_folder"])
    options["midi_device_no"] = int(config["PLAY_OPTIONS"]["midi_device_no"])
    options["image_width"] = int(config["SHARED_OPTIONS"]["screen_width"])
    options["image_height"] = int(config["SHARED_OPTIONS"]["screen_height"])
    return options


def replace_options_from_command_line(options, args):
    true_strings = misc_helpers.get_true_strings()
    if args["song"]:
        options["song"] = args["song"]
    if args["left"]:
        options["play_left"] = True if args["left"] in true_strings else False
    if args["right"]:
        options["play_right"] = True if args["right"] in true_strings else False
    if args["device"]:
        options["midi_device_no"] = int(args["device"])
    if args["present"]:
        options["presentation_mode"] = True if args["present"] in true_strings else False

def create_complete_paths(options):
    hand_string = misc_helpers.get_folder_hand_string(options)
    options["song_folder_complete"] = os.path.join(options["songs_folder"], options["song"], hand_string) + "/"




def get_options():
    parser = get_parser()
    parsed_arguments = vars(parser.parse_args())
    filename = parsed_arguments["config"]
    config = get_config(filename)
    options = get_options_from_config(config)

    replace_options_from_command_line(options, parsed_arguments)
    create_complete_paths(options)

    return options
