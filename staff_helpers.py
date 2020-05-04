import mingus.containers
import re
import mingus.core.intervals

def remove_comments(src):
    # src_clean = ""
    # for line in src.split("\n"):
    #     src_clean += line.split("#")[0] + "\n"
    src_clean = re.sub(re.compile("%{.*?%}",re.DOTALL ), "" , src)
    return src_clean

def get_staff_strings(content):
    staff_strings = []
    fragments = [f.strip() for f in content.split("\\new Staff {")]
    fragments = fragments[1:]
    for index, f in enumerate(fragments):
        if index < len(fragments) - 1:
            f = f[:-2]
            staff_strings.append(f)
        else:
            f = f[:-4]
            staff_strings.append(f)
    return staff_strings


def create_color_string(action_notes, chord_root, staff_index):
    staff_index_str = "-" + str(staff_index)
    color_mapping = get_color_mapping(action_notes, chord_root, staff_index_str)
    color_string = " " + color_mapping
    color_string += "#(define (pitch-equals? p1 p2) \n"
    color_string += "(and \n"
    color_string += "(= (ly:pitch-alteration p1) (ly:pitch-alteration p2)) \n"
    color_string += "(= (ly:pitch-octave p1) (ly:pitch-octave p2)) \n"
    color_string += "(= (ly:pitch-notename p1) (ly:pitch-notename p2)) \n"
    color_string += "))"
    color_string += "\n"
    color_string += "#(define (pitch-to-color%s pitch) \n" % staff_index_str
    color_string += "(let ((color (assoc pitch color-mapping%s pitch-equals?))) \n" % staff_index_str
    color_string += "(if color \n"
    color_string += "(cdr color)))) \n"
    color_string += ""
    color_string += "#(define (color-notehead%s grob) \n" % staff_index_str
    color_string += "(pitch-to-color%s \n" % staff_index_str
    color_string += "(ly:event-property (ly:grob-property grob 'cause) 'pitch))) \n"
    color_string += "\n"
    color_string += "\\once \\override NoteHead #'color = #color-notehead%s \n" % staff_index_str
    return color_string

def get_color_mapping(action_notes, chord_root, staff_index_str):
    color_mapping = ""
    color_mapping += "\n#(define color-mapping%s\n" % staff_index_str
    color_mapping += "(list\n"

    root_dict = { "c": 0, "d": 1, "e": 2, "f": 3, "g": 4, "a": 5, "b": 6 }
    alterations_dict = { 0: "", 1: "1/2", 2: "1", -1: "-1/2", -2: "-1" }
    for a in action_notes:
        octave = a.count("'") - 1 - a.count(",")
        alteration = a.count("is") * 1 - a.count("es")
        root_str = a.replace("'", "").replace(",","").replace("is", "").replace("es", "")
        root = root_dict[root_str]
        alteration_str = alterations_dict[alteration]
        # print("test", a, octave, alteration, root)
        if chord_root:
            note_color = get_note_color(a.replace("'", "").replace(",",""), chord_root)
        else:
            note_color = "blue"
        color_mapping += "(cons (ly:make-pitch %i %i %s) (x11-color '%s))\n" % ( octave, root, alteration_str, note_color)

    color_mapping += "))\n\n"
    #print(color_mapping)
    return color_mapping

def get_color_dictionary():
    color_dict = {}
    color_dict[0] = "blue" # LightSlateGrey
    color_dict[1] = "blue"
    color_dict[2] = "blue"
    color_dict[3] = "red"  # kleine terz
    color_dict[4] = "red" # grosse terz
    color_dict[5] = "blue"
    color_dict[6] = "blue"
    color_dict[7] = "blue" # quinte
    color_dict[8] = "blue"
    color_dict[9] = "blue"
    color_dict[10] = "LimeGreen"
    color_dict[11] = "LimeGreen"
    return color_dict

def get_note_color(note_str, chord_root):
    mingus_chord_root = convert_to_mingus_root_notation(chord_root)
    mingus_note_str = convert_to_mingus_root_notation(note_str)

    distance = mingus.core.intervals.measure(mingus_chord_root, mingus_note_str) # immer positiv

    #print("interval", mingus_chord_root, mingus_note_str, distance)
    note_color = get_color_dictionary()[distance]
    return note_color

def convert_to_mingus_root_notation(note_str):
    tmp = note_str.replace("'", "").replace(",", "").replace("es", "b").replace("is", "#")
    tmp = tmp[0].upper() + tmp[1:]
    return tmp

def get_mingus_notes(actions):
    mingus_notes = []
    for a in actions:
        octave = a.count("'") - a.count(",")
        note_string = a.replace("'", "").replace(",", "")
        note_string = note_string.replace("es", "b").replace("is", "#")
        note_string = note_string[0].upper() + note_string[1:]
        mingus_note = mingus.containers.Note(note_string, octave + 4)
        #print("mingus", mingus_note)
        mingus_notes.append(mingus_note)
    return mingus_notes



def get_normalized_staff_strings(staffs):
    normalized = []
    for s in staffs:
        s = get_staff_string_without_unwanted_commands(s)
        s = get_with_normalized_spaces(s)
        s = s.replace(" ~", "~")
        s = get_without_repeats(s)

        s.replace("  ", " ") # sicherheitshalber
        #print(s)
        #print("\n"*10)
        normalized.append(s)
    return normalized



def get_with_normalized_spaces(s):
    s = " " + s
    s = s.replace(" >", ">")
    s = s.replace(" < ", " <")
    s = s.replace(">>", " >>")
    s = s.replace("  ", " ")
    s = s.strip()
    return s

def get_staff_string_without_unwanted_commands(s):
    commands = []
    # commands.append("")
    # commands.append("\")

    commands.append("\\override Staff.NoteCollision.merge-differently-dotted = ##t")
    commands.append("\\!")
    commands.append("\\>")
    commands.append("\\<")
    commands.append("\\revert NoteColumn.horizontal-shift")
    commands.append("\\revert Stem.direction")
    commands.append("\\override Stem.direction = #-1")
    commands.append("\\override Stem.direction = #1")
    commands.append("\\break")
    commands.append("\\pageBreak")
    commands.append("\\revert NoteColumn.horizontal-shift")
    for c in commands:
        s = s.replace(c, "")
    return s


def get_number_of_repeats(position, repeat_string, s):
    tmp = ""
    i = 1
    while True:
        digit_character = s[position + len(repeat_string) + i]
        if digit_character != " ":
            tmp += digit_character
            i += 1
        else:
            break
    return int(tmp)


def get_position_of_closing_bracket(start_position, s, start_bracket="{", end_bracket="}"):
    number_open = 1
    number_close = 0
    current_position = start_position
    while number_open != number_close:
        current_position += 1
        character = s[current_position]
        if character == start_bracket:
            number_open += 1
        elif character == end_bracket:
            number_close += 1
    #print("test", s[start_position], current_position)
    return current_position

def get_without_repeats(s):
    unfolded = ""
    repeat_string = "repeat volta"
    positions = [m.start() for m in re.finditer(repeat_string, s)]

    index_start_copy = 0
    if len(positions) > 0:
        #print(s)
        for position in positions:
            number_of_repeats = get_number_of_repeats(position, repeat_string, s)
            start_position = position + len(repeat_string) + 2 + len(str(number_of_repeats))
            position_of_closing_bracket = get_position_of_closing_bracket(start_position, s)
            string_to_be_repeated = s[start_position + 1: position_of_closing_bracket].strip()
            contains_alternative = s[position_of_closing_bracket + 2:].startswith("\\alternative")
            alternatives = [""] * number_of_repeats
            if contains_alternative:
                alternative_bracket_start_position = position_of_closing_bracket + 2 + len("\\alternative") + 2
                alternative_bracket_end_position = get_position_of_closing_bracket(alternative_bracket_start_position, s)
                alternative_string = s[alternative_bracket_start_position + 1:alternative_bracket_end_position].strip()
                alternatives = []
                current_alternative_start = 0
                for i in range(number_of_repeats):
                    current_alternative_end_position = get_position_of_closing_bracket(current_alternative_start, alternative_string)
                    current_alternative_string = alternative_string[current_alternative_start + 1:current_alternative_end_position].strip()
                    current_alternative_start = current_alternative_end_position + 2
                    alternatives.append(current_alternative_string)

            # now add to unfolded string
            unfolded += s[index_start_copy:position-1]
            for i in range(number_of_repeats):
                unfolded += string_to_be_repeated + " "
                unfolded += alternatives[i] + " "

            if contains_alternative:
                index_start_copy = alternative_bracket_end_position + 2
            else:
                index_start_copy = position_of_closing_bracket + 2

        return unfolded
    else:
        return s
