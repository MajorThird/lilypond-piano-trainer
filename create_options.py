import argparse
import configparser

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
    return parser




def normalize_folder_string(folder):
    """
    Make sure that the folder names given in the input file
    contain / at the end.
    """
    if folder[-1] == "/":
        return folder
    else:
        return folder + "/"


def get_options_from_config(config):
    # used to convert option strings to boolean
    true_strings = ["True", "true", "t", "T", "1"]

    options = {}
    options["song"] = config["MAKE_OPTIONS"]["song"]
    options["play_right"] = True if config["MAKE_OPTIONS"]["play_right"] in true_strings else False
    options["play_left"] = True if config["MAKE_OPTIONS"]["play_left"] in true_strings else False
    options["in_folder"] = normalize_folder_string(config["MAKE_OPTIONS"]["in_folder"])
    options["out_folder"] = normalize_folder_string(config["MAKE_OPTIONS"]["out_folder"])
    options["image_width"] = int(config["MAKE_OPTIONS"]["image_width"])
    options["image_height"] = int(config["MAKE_OPTIONS"]["image_height"])

    return options


def replace_options_from_command_line(options, args):
    true_strings = ["True", "true", "t", "T", "1"]
    if args["song"]:
        options["song"] = args["song"]
    if args["left"]:
        options["play_left"] = True if args["left"] in true_strings else False
    if args["right"]:
        options["play_right"] = True if args["right"] in true_strings else False

def get_options():
    parser = get_parser()
    parsed_arguments = vars(parser.parse_args())
    filename = parsed_arguments["config"]
    config = get_config(filename)
    options = get_options_from_config(config)
    replace_options_from_command_line(options, parsed_arguments)
    return options
