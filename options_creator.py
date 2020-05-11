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
        help="use this song instead of the one in the config file [don't write the extension .ly]")
    parser.add_argument("-r", "--right",
        required=False,
        help="create song for the right hand [possible values: 0,1]")
    parser.add_argument("-l", "--left",
        required=False,
        help="create song for the left hand [possible values: 0,1]")
    parser.add_argument("-i", "--infolder",
        required=False,
        help="folder containing the lilypond files")
    return parser




def get_options_from_config(config):
    true_strings = misc_helpers.get_true_strings()

    options = {}
    options["song"] = config["MAKE_OPTIONS"]["song"]
    options["play_right"] = True if config["MAKE_OPTIONS"]["play_right"] in true_strings else False
    options["play_left"] = True if config["MAKE_OPTIONS"]["play_left"] in true_strings else False
    options["in_folder"] = misc_helpers.normalize_folder_string(config["MAKE_OPTIONS"]["in_folder"])
    options["out_folder"] = misc_helpers.normalize_folder_string(config["MAKE_OPTIONS"]["out_folder"])
    options["image_width"] = int(config["SHARED_OPTIONS"]["screen_width"])
    options["image_height"] = int(config["SHARED_OPTIONS"]["screen_height"])
    options["image_resolution"] = int(config["MAKE_OPTIONS"]["image_resolution"])
    return options


def replace_options_from_command_line(options, args):
    true_strings = misc_helpers.get_true_strings()
    if args["song"]:
        options["song"] = args["song"]
    if args["left"]:
        options["play_left"] = True if args["left"] in true_strings else False
    if args["right"]:
        options["play_right"] = True if args["right"] in true_strings else False
    if args["infolder"]:
        options["in_folder"] = misc_helpers.normalize_folder_string(args["infolder"])

def create_complete_paths(options):
    hand_string = misc_helpers.get_folder_hand_string(options)
    options["output_folder_complete"] = os.path.join(options["out_folder"], options["song"], hand_string) + "/"
    options["lily_file"] = os.path.join(options["in_folder"], options["song"] + ".ly")


def get_options():
    parser = get_parser()
    parsed_arguments = vars(parser.parse_args())
    filename = parsed_arguments["config"]
    config = get_config(filename)
    options = get_options_from_config(config)


    replace_options_from_command_line(options, parsed_arguments)
    create_complete_paths(options)
    options["staff_activations"] = [options["play_right"], options["play_left"]]

    return options
