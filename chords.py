import staff_helpers
from fractions import Fraction


class Chord(object):
    def __init__(self, root=None, duration=None, time=None, full_string=None):
        self.root = root
        self.duration = duration
        self.time = time
        self.full_string = full_string


def get_chords(filename):
    with open(filename) as infile:
        content = infile.read()
        content = staff_helpers.remove_comments(content)
        content = content.replace("{", "{ ")
        content = content.replace("}", " }")
        content = content.replace("\n", " ")
        content = " ".join(content.split())

    chords = []
    chord_strings = get_chord_strings(content)
    time = Fraction(0)
    duration = Fraction(1,4)
    for s in chord_strings:
        root = get_root(s)
        duration = get_duration(s, duration)
        full_string = add_duration_to_string(s, duration)
        c = Chord(root=root, duration=duration, time=time, full_string=full_string)
        chords.append(c)
        time = time + duration
    return chords

def add_duration_to_string(s, duration):
    tmp = s.split(":")
    denominator = "".join([c for c in tmp[0] if c.isdigit()])
    if denominator != "":
        return s
    else:
        denominator = str(duration.denominator)
        front = tmp[0] + denominator
        if len(tmp) > 1:
            return front + ":" + tmp[1]
        else:
            return front

def get_dot_factor(e):
    if "...." in e:
        n = 4
    elif "..." in e:
        n = 3
    elif ".." in e:
        n = 2
    elif "." in e:
        n = 1
    else:
        n = 0
    tmp = Fraction(1,2**n)
    factor = Fraction(2,1) - tmp
    return factor

def get_duration(s, previous_duration):
    tmp = s.split(":")[0]
    dot_factor = get_dot_factor(tmp)
    denominator = "".join([c for c in tmp if c.isdigit()])
    if denominator == "":
        return previous_duration
    else:
        duration = Fraction(1, int(denominator)) * dot_factor
        return duration


def get_root(s):
    root = s.split(":")[0]
    root = ''.join([c for c in root if not c.isdigit()])
    root = root.replace(".", "")
    return root


def get_chord_strings(s):
    if "\\chords {" in s:
        chord_strings = s.split("\\chords {")[1]
        chord_strings = chord_strings.split("\\new Staff {")[0]
        chord_strings = chord_strings.split("}")[0].strip()
        chord_strings = chord_strings.split(" ")
        return chord_strings
    else:
        return []
